from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.speech import router as speech_router

# Load environment variables
load_dotenv()

app = FastAPI()

# Frontend URLs from .env
FRONTEND_DEV_URL = os.getenv("FRONTEND_DEV_URL")
FRONTEND_PROD_URL = os.getenv("FRONTEND_PROD_URL")

# Allow only approved frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_DEV_URL,
        FRONTEND_PROD_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(speech_router)

@app.get("/")
def home():
    return {"message": "Admission Bot Backend Running"}