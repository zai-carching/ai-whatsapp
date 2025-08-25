from fastapi import FastAPI, Request
from openai import OpenAI
from pinecone import Pinecone
from app import routes

import config

app = FastAPI()
openai = OpenAI(api_key=config.OPENAI_API_KEY)
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.INDEX_NAME)

app.include_router(routes.router)
@app.get("/")
def get_root():
    return {"message": "Hello World"}