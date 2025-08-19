import os
import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

import config

st.set_page_config(page_title="Carching Support", page_icon="🚗")

try:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    index = pc.Index(config.DEMO_INDEX_NAME)
except Exception as e:
    st.error(f"Failed to initialize services: {str(e)}")
    st.stop()

st.sidebar.header("⚙️ Settings")

default_prompt = config.SYSTEM_PROMPT

system_prompt_template = st.sidebar.text_area("📝 System Prompt", value=default_prompt, height=250)

model_choice = st.sidebar.selectbox(
    "🤖 Select Model",
    ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "gpt-4-turbo","gpt-5-mini"]
)

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()


def retrieve_context(query: str) -> str:
    try:
        # Embed the query
        emb = client.embeddings.create(
            model=config.EMBED_MODEL,
            input=query
        ).data[0].embedding

        # Query Pinecone for nearest chunks
        result = index.query(
            vector=emb,
            top_k=getattr(config, "TOP_K", 5),
            include_metadata=True,
            include_values=False,
            namespace=getattr(config, "NAMESPACE", None)
        )

        matches = getattr(result, "matches", []) or []
        if not matches:
            return ""

        min_score = getattr(config, "MIN_SCORE", 0.0)
        max_chars = getattr(config, "MAX_CONTEXT_CHARS", 8000)

        # Build compact, provenance-rich context
        contexts = []
        total = 0
        for m in matches:
            score = getattr(m, "score", None)
            if score is not None and score < min_score:
                continue

            meta = m.metadata or {}
            text = meta.get("text") or ""
            if not text:
                continue

            file_name = meta.get("file_name", "")
            chunk_num = meta.get("chunk_num")
            header = f"Source: {file_name}" + (f" (chunk {chunk_num})" if chunk_num is not None else "")
            snippet = f"{header}\n{text}" if header.strip() else text

            if total + len(snippet) > max_chars:
                break

            contexts.append(snippet)
            total += len(snippet)

        return "\n\n---\n\n".join(contexts)
    except Exception as e:
        st.warning(f"Couldn't retrieve context: {str(e)}")
        return ""

# Function to get chatbot response
def respond(message, chat_history):
    try:
        context = retrieve_context(message)
        system_prompt = system_prompt_template.format(context=context)

        messages = [
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": message}
        ]

        response = client.chat.completions.create(
            model=model_choice,
            messages=messages,
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content

        updated_history = chat_history[-4:] + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": bot_reply}
        ]

        return updated_history
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return chat_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "Sorry, I encountered an error. Please try again."}
        ]

# App Title
st.title("🚗 Carching Customer Support")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat messages
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about Carching..."):
    st.chat_message("user").markdown(prompt)

    with st.spinner("Thinking..."):
        st.session_state.chat_history = respond(
            prompt,
            st.session_state.chat_history
        )

    st.chat_message("assistant").markdown(st.session_state.chat_history[-1]["content"])