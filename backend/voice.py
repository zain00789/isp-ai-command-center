
import os
import tempfile
import base64

from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response, JSONResponse
from faster_whisper import WhisperModel
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

from backend.ai_chat import ChatRequest, chat_with_ai

load_dotenv()

router = APIRouter(prefix="/api/v1/voice", tags=["Voice"])

whisper_model = None

ELEVENLABS_VOICE_ID = "cjVigY5qzO86Huf0OWal"
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"


def get_whisper_model():
    global whisper_model

    if whisper_model is None:
        whisper_model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

    return whisper_model


def generate_elevenlabs_audio(text: str) -> bytes:
    """Generate MP3 audio using ElevenLabs Eric voice."""

    client = ElevenLabs(
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )

    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        model_id=ELEVENLABS_MODEL_ID,
        text=text,
        voice_settings=VoiceSettings(
            stability=0.35,
            similarity_boost=0.75,
            style=0.25,
            use_speaker_boost=True
        )
    )

    return b"".join(audio)


@router.get("/health")
def voice_health():
    return {
        "status": "ok",
        "service": "voice",
        "mode": "real"
    }


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):

    allowed_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/ogg",
        "audio/mp4",
        "audio/webm",
        "video/ogg",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail="Unsupported audio format"
        )

    audio_data = await file.read()

    if not audio_data:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty"
        )

    if len(audio_data) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file exceeds the 10 MB limit"
        )

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_audio:
        temp_audio.write(audio_data)
        audio_path = temp_audio.name

    try:
        model = get_whisper_model()
        segments, info = model.transcribe(
        audio_path,
        language="ur",
        initial_prompt="Mera internet slow chal raha hai. Wi-Fi, router, internet speed, connection aur package.",
        beam_size=5
    )

        transcribed_text = " ".join(
            segment.text for segment in segments
        ).strip()

    finally:
        os.unlink(audio_path)

    return {
        "status": "success",
        "text": transcribed_text,
        "language": info.language,
        "mode": "real"
    }


class VoiceChatRequest(BaseModel):
    text: str
    session_id: str


@router.post("/chat")
def voice_chat(request: VoiceChatRequest):
    chat_request = ChatRequest(
        message=request.text,
        session_id=request.session_id
    )

    return chat_with_ai(chat_request)


@router.post("/ask")
async def ask_ai_by_voice(
    file: UploadFile = File(...),
    session_id: str = "voice-session"
):
    transcription = await transcribe_audio(file)
    text = transcription["text"]

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No speech detected in audio"
        )

    chat_request = ChatRequest(
        message=text,
        session_id=session_id
    )

    ai_result = chat_with_ai(chat_request)

    return {
        "status": "success",
        "transcription": text,
        "language": transcription["language"],
        "ai": ai_result
    }


@router.post("/speak")
async def speak_text(request: VoiceChatRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    if len(text) > 2000:
        raise HTTPException(
            status_code=413,
            detail="Text exceeds 2000 characters"
        )

    try:
        audio_data = await run_in_threadpool(
            generate_elevenlabs_audio,
            text
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Voice generation failed"
        )

    if not audio_data:
        raise HTTPException(
            status_code=502,
            detail="Speech generation returned no audio"
        )

    return Response(
        content=audio_data,
        media_type="audio/mpeg"
    )


@router.post("/ask-and-speak")
async def ask_and_speak(
    file: UploadFile = File(...),
    session_id: str = "voice-session"
):
    transcription = await transcribe_audio(file)
    text = transcription["text"]

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No speech detected in audio"
        )

    chat_request = ChatRequest(
        message=text,
        session_id=session_id
    )

    ai_result = chat_with_ai(chat_request)

    response_text = ai_result["response"]

    if not response_text.strip():
        raise HTTPException(
            status_code=502,
            detail="AI returned an empty response"
        )

    if len(response_text) > 2000:
        raise HTTPException(
            status_code=413,
            detail="AI response exceeds voice generation limit"
        )

    try:
        audio_data = await run_in_threadpool(
            generate_elevenlabs_audio,
            response_text
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Voice generation failed"
        )

    if not audio_data:
        raise HTTPException(
            status_code=502,
            detail="Speech generation returned no audio"
        )

    return JSONResponse({
        "status": "success",
        "transcription": text,
        "language": transcription["language"],
        "ai": ai_result,
        "audio_base64": base64.b64encode(audio_data).decode("ascii"),
        "audio_format": "mp3"
    })
