
### Translation Service Implementation:

```python
# src/backend/ai/translation/service.py
import os
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Translation Service")

# Models for requests and responses
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    model: Optional[str] = "nemo-mt"

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    processing_time: float
    model_used: str

# NeMo Translation model setup
try:
    import nemo.collections.nlp as nemo_nlp
    
    # Load pre-trained models - adjust model names as needed
    model_map = {
        "en-de": nemo_nlp.models.machine_translation.MTEncDecModel.from_pretrained("nmt_en_de_transformer24x6"),
        "en-es": nemo_nlp.models.machine_translation.MTEncDecModel.from_pretrained("nmt_en_es_transformer12x2"),
        # Add more language pairs as needed
    }
    
    logger.info(f"Loaded {len(model_map)} NeMo translation models")
except Exception as e:
    logger.error(f"Failed to initialize NeMo translation models: {str(e)}")
    model_map = {}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "translation-service",
        "available_models": list(model_map.keys())
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text using NeMo models"""
    # Create language pair key
    lang_pair = f"{request.source_language}-{request.target_language}"
    
    if not model_map:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    if lang_pair not in model_map:
        raise HTTPException(status_code=400, detail=f"Unsupported language pair: {lang_pair}")
    
    try:
        start_time = datetime.now()
        
        # Get the appropriate model
        model = model_map[lang_pair]
        
        # Perform translation
        translated_text = model.translate([request.text])[0]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return TranslationResponse(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
            processing_time=processing_time,
            model_used=lang_pair
        )
    
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supported-languages")
def supported_languages():
    """List supported language pairs"""
    language_pairs = list(model_map.keys())
    
    # Extract unique languages
    languages = set()
    for pair in language_pairs:
        src, tgt = pair.split('-')
        languages.add(src)
        languages.add(tgt)
    
    return {
        "supported_pairs": language_pairs,
        "languages": list(languages)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run("translation.service:app", host="0.0.0.0", port=port, reload=False)
```