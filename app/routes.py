from fastapi import APIRouter, Request
import config
from . import llm
router = APIRouter()

@router.get("/ping")
def ping():
    dummy_history = []
    updated_history, reply = llm.generate(
        "How much can i earn at carching?",
        dummy_history,
        config.SYSTEM_PROMPT,
        config.CHAT_MODEL
    )
    return {"message": reply}

@router.get("/whatsapp/webhook")
async def whatsapp_webhook_get():
    pass

@router.post("/whatsapp/webhook")
async def whatsapp_webhook_post():
    pass
