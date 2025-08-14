from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv(verbose=True)

app = FastAPI()

@app.get("/")
def get_root():
    return {"message": "Hello World"}