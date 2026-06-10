from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import whisper
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

API_KEY = os.getenv("API_KEY")

# Load whisper model
model = whisper.load_model("base")

@router.post("/speech-to-text")
async def speech_to_text(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # Check API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Save uploaded audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Transcribe audio
    result = model.transcribe(tmp_path)
    os.remove(tmp_path)

    return {
        "text": result["text"],
        "language": result["language"]
    }