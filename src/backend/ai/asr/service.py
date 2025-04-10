
### ASR Service Implementation:

```python
# src/backend/ai/asr/service.py
import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
import aiofiles
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ASR Service")

# Models for requests and responses
class TranscriptionRequest(BaseModel):
    audio_path: str
    language: Optional[str] = "en-US"
    model: Optional[str] = "riva-asr"
    punctuation: bool = True
    profanity_filter: bool = False

class TranscriptionResponse(BaseModel):
    text: str
    confidence: float
    language: str
    processing_time: float
    word_timestamps: Optional[List[Dict[str, Any]]] = None

# Riva ASR client setup
try:
    import riva.client
    riva_client = riva.client.ASRClient(
        uri="localhost:50051",
        use_ssl=False,
        ssl_cert=None
    )
    logger.info("Riva ASR client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Riva ASR client: {str(e)}")
    riva_client = None

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "asr-service",
        "riva_available": riva_client is not None
    }

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio using Riva ASR"""
    if not riva_client:
        raise HTTPException(status_code=503, detail="ASR service not available")
    
    try:
        start_time = datetime.now()
        
        # Read audio file
        with open(request.audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Configure ASR parameters
        config = riva.client.ASRConfig()
        config.language_code = request.language
        config.enable_automatic_punctuation = request.punctuation
        config.profanity_filter = request.profanity_filter
        config.audio_encoding = riva.client.AudioEncoding.LINEAR_PCM
        
        # Perform transcription
        response = riva_client.offline_recognize(
            audio_data,
            config=config
        )
        
        # Process results
        best_result = response.results[0] if response.results else None
        if not best_result:
            raise HTTPException(status_code=500, detail="No transcription result")
        
        text = best_result.alternatives[0].transcript
        confidence = best_result.alternatives[0].confidence
        
        # Extract word timestamps if available
        word_timestamps = []
        if best_result.alternatives[0].words:
            for word_info in best_result.alternatives[0].words:
                word_timestamps.append({
                    "word": word_info.word,
                    "start_time": word_info.start_time.ToSeconds(),
                    "end_time": word_info.end_time.ToSeconds(),
                    "confidence": word_info.confidence
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return TranscriptionResponse(
            text=text,
            confidence=confidence,
            language=request.language,
            processing_time=processing_time,
            word_timestamps=word_timestamps
        )
    
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/upload")
async def transcribe_uploaded_audio(
    language: str = "en-US",
    model: str = "riva-asr",
    punctuation: bool = True,
    profanity_filter: bool = False,
    file: UploadFile = File(...)
):
    """Transcribe uploaded audio file"""
    if not riva_client:
        raise HTTPException(status_code=503, detail="ASR service not available")
    
    try:
        # Create a temporary file to store the uploaded audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_audio_path = f"/app/data/temp_audio_{timestamp}.wav"
        
        # Save uploaded file
        async with aiofiles.open(temp_audio_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Create request for transcription
        request = TranscriptionRequest(
            audio_path=temp_audio_path,
            language=language,
            model=model,
            punctuation=punctuation,
            profanity_filter=profanity_filter
        )
        
        # Process transcription
        result = await transcribe_audio(request)
        
        # Clean up temporary file
        os.remove(temp_audio_path)
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing uploaded audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("asr.service:app", host="0.0.0.0", port=port, reload=False)
```