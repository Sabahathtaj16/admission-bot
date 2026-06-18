from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from database import get_connection
from redis_client import redis_client
import os
import re
import unicodedata

router = APIRouter()

API_KEY = os.getenv("API_KEY")


class Message(BaseModel):
    text: str


def normalize_text(text: str):
    text = unicodedata.normalize("NFC", text)
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


@router.post("/chat")
def chat(msg: Message, x_api_key: str = Header(None)):

    # API Key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    user_input = normalize_text(msg.text)

    try:
        # Redis cache key
        cache_key = f"faq:{user_input}"

        # Check cache first
        cached_reply = redis_client.get(cache_key)
        if cached_reply:
            return {"reply": cached_reply}

        # DB connection
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT answer FROM faqs WHERE question LIKE %s",
            (f"%{user_input}%",)
        )

        result = cursor.fetchone()
        conn.close()

        if result:
            reply = result[0]

            # Save to Redis (1 hour cache)
            redis_client.setex(cache_key, 3600, reply)

            return {"reply": reply}

        return {"reply": "Sorry, I couldn't find an answer to your question."}

    except Exception:
        return {"reply": "Database not connected yet. Please try again later."}