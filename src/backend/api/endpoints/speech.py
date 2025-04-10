# src/backend/api/endpoints/speech.py
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
import httpx
import os

router = APIRouter()

ASR_SERVICE_URL = os.getenv("ASR_SERVICE_URL", "http://asr-layer:8001")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://tts-layer:8002")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_SERVICE_URL", "http://translation-layer:8003")

@router.post("/asr/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en-US"),
    punctuation: bool = Form(True),
    profanity_filter: bool = Form(False)
):
    """Endpoint to transcribe audio via ASR service"""
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            params = {
                "language": language,
                "punctuation": str(punctuation).lower(),
                "profanity_filter": str(profanity_filter).lower()
            }
            
            response = await client.post(
                f"{ASR_SERVICE_URL}/transcribe/upload",
                files=files,
                params=params
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    language: str = Form("en-US"),
    voice: str = Form("female-1"),
    speaking_rate: float = Form(1.0),
    pitch: float = Form(0.0)
):
    """Endpoint to synthesize speech via TTS service"""
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "text": text,
                "language": language,
                "voice": voice,
                "speaking_rate": speaking_rate,
                "pitch": pitch
            }
            
            response = await client.post(
                f"{TTS_SERVICE_URL}/synthesize",
                json=data
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def translate_text(
    text: str = Form(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):
    """Endpoint to translate text via Translation service"""
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language
            }
            
            response = await client.post(
                f"{TRANSLATION_SERVICE_URL}/translate",
                json=data
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))