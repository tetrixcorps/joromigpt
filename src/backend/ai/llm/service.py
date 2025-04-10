# src/backend/ai/llm/service.py
import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="LLM Service")

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3-2-instruct")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model_registry/llama-3.2")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize model and tokenizer
tokenizer = None
model = None

@app.on_event("startup")
async def startup_event():
    global tokenizer, model
    try:
        logger.info(f"Loading model {MODEL_NAME} from {MODEL_PATH}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            device_map="auto" if DEVICE == "cuda" else None,
        )
        logger.info(f"Model loaded successfully on {DEVICE}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = Field(1024, ge=1, le=MAX_TOKENS)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    stop: Optional[List[str]] = []

class GenerationResponse(BaseModel):
    generated_text: str
    model_used: str
    tokens_generated: int

async def generate_text_with_model(
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop: Optional[List[str]] = None
) -> str:
    """Generate text using the loaded LLM model."""
    if model is None or tokenizer is None:
        raise RuntimeError("Model or tokenizer not initialized")
    
    stop_tokens = stop or []
    
    try:
        # Tokenize the input
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=temperature > 0,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode the generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the input prompt from the output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):]
        
        # Apply stop sequences
        if stop_tokens:
            for stop_token in stop_tokens:
                if stop_token in generated_text:
                    generated_text = generated_text.split(stop_token)[0]
        
        return generated_text
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(request: dict):
    """Endpoint for LangChain adapter to generate text"""
    try:
        prompt = request.get("prompt", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt provided")
            
        # Get other parameters
        stop = request.get("stop", [])
        max_tokens = request.get("max_tokens", 1024)
        temperature = request.get("temperature", 0.7)
        top_p = request.get("top_p", 0.9)
        
        # Generate text
        generated_text = await generate_text_with_model(
            prompt=prompt,
            stop=stop,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        return {
            "generated_text": generated_text,
            "model_used": MODEL_NAME,
            "tokens_generated": len(tokenizer.encode(generated_text))
        }
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for the LLM service."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=5000, reload=True)