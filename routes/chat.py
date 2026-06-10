from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from database import get_connection
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

API_KEY = os.getenv("API_KEY")

class Message(BaseModel):
    text: str

@router.post("/chat")
def chat(msg: Message, x_api_key: str = Header(None)):
    
    # Check API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    user_input = msg.text.lower()
    
    try:
        # Connect to database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Search for answer in database
        cursor.execute(
            "SELECT answer FROM faqs WHERE LOWER(question) LIKE %s",
            (f"%{user_input}%",)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"reply": result[0]}
        else:
            return {"reply": "Sorry, I couldn't find an answer to your question."}
    
    except Exception as e:
        # If DB not connected yet, return this
        return {"reply": "Database not connected yet. Please try again later."}