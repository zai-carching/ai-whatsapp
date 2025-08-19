import os
import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

import config

st.set_page_config(page_title="Carching Support", page_icon="🚗")

try:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    index = pc.Index("web-data")
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


def retrieve_context(query):
    try:
        response = client.embeddings.create(
            model=config.EMBED_MODEL,
            input=query
        )
        query_emb = response.data[0].embedding

        result = index.query(
            vector=query_emb,
            top_k=config.TOP_K,
            include_metadata=True
        )

        contexts = []
        for match in result.matches:
            meta = match.metadata
            context_str = f"Title: {meta['title']}\nContent: {meta['content']}"
            contexts.append(context_str)

        return "\n\n".join(contexts)
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