from fastapi import FastAPI, Request
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

import config

app = FastAPI()
openai = OpenAI(api_key=config.OPENAI_API_KEY)
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.INDEX_NAME)
@app.get("/")
def get_root():
    return {"message": "Hello World"}