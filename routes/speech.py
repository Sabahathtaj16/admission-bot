from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import whisper
import os
import tempfile
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

API_KEY = os.getenv("API_KEY")

# Load Whisper model once when the application starts
model = whisper.load_model("base")


@router.post("/speech-to-text")
async def speech_to_text(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # Validate API key
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    tmp_path = None

    try:
        # Save uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Run Whisper transcription in a separate thread
        # so FastAPI's event loop is not blocked
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            None,
            lambda: model.transcribe(tmp_path)
        )

        return {
            "text": result["text"],
            "language": result["language"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Speech transcription failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)