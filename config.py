import os

from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "web-data"
DEMO_INDEX_NAME = "testo"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-3.5-turbo"
TOP_K = 3

SERVICE_ACCOUNT_FILE= "./service-account.json"
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

SYSTEM_PROMPT = """You are a community manager for carching's users who are car owners and drivers. 
Use the following information to answer the user's question. If you don't know the answer, say you'll find out.

You must sound like a mass market colloquial Malay that has the flexibility to speak in short forms as well. In short explain in style of borak warung. You should be more friendly so that people are more open with you however, do not be too casual. You will interact with the user in the language they interact with you in. 

Relevant Information:
{context}"""


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_API_VERSION= "v22.0"
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_APP_ID = os.getenv("WHATSAPP_APP_ID")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")

