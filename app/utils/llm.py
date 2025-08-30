from openai import OpenAI
from pinecone import Pinecone
import config


# Initialize clients once
client = OpenAI(api_key=config.OPENAI_API_KEY)
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.DEMO_INDEX_NAME)


# -------------------------------
# Helpers
# -------------------------------

def embed_text(text: str):
    """Generate embedding for a given text."""
    return client.embeddings.create(
        model=config.EMBED_MODEL,
        input=text
    ).data[0].embedding


def fetch_context(query: str) -> str:
    """Retrieve context from Pinecone for a query."""
    try:
        emb = embed_text(query)

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

        contexts, total = [], 0
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

    except Exception:
        return ""


def build_messages(message: str, chat_history: list, system_prompt_template: str, context: str):
    """Construct messages for the LLM."""
    system_prompt = system_prompt_template.format(context=context)
    return [
        {"role": "system", "content": system_prompt},
        *chat_history,
        {"role": "user", "content": message},
    ]


def ask_llm(messages: list, model_choice: str) -> str:
    """Send messages to OpenAI and return reply."""
    response = client.chat.completions.create(
        model=model_choice,
        messages=messages,
        # temperature=0.7,
    )
    return response.choices[0].message.content


def update_history(chat_history: list, user_message: str, bot_reply: str):
    """Update conversation history with new messages."""
    return chat_history[-4:] + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_reply},
    ]


# -------------------------------
# Main generate function
# -------------------------------

def generate(message: str, chat_history: list, system_prompt_template: str, model_choice: str):
    """Main entry point to generate a response."""
    try:
        context = fetch_context(message)
        messages = build_messages(message, chat_history, system_prompt_template, context)
        bot_reply = ask_llm(messages, model_choice)
        updated_history = update_history(chat_history, message, bot_reply)
        return updated_history, bot_reply

    except Exception as e:
        fallback = f"Sorry, I encountered an error: {str(e)}"
        return update_history(chat_history, message, fallback), fallback
