# docker/adapters/nvclip-adapter/app.py
import base64
import io
import json
import os
import requests
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn

app = FastAPI(title="NV-CLIP Adapter for Ollama")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NVCLIP_URL = os.environ.get("NVCLIP_URL", "http://nvclip:3456")

def process_image(image_data: bytes) -> Dict[str, Any]:
    """Process an image through NV-CLIP and return embeddings"""
    try:
        # Convert to base64 for API call
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Call NV-CLIP API
        response = requests.post(
            f"{NVCLIP_URL}/v1/embeddings",
            json={
                "input": [
                    {
                        "type": "image",
                        "data": encoded_image
                    }
                ]
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"NV-CLIP API error: {response.text}")
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def ollama_completions_proxy(
    prompt: str = Form(...),
    image: Optional[UploadFile] = File(None),
    system: Optional[str] = Form(None),
    template: Optional[str] = Form(None)
):
    """Proxy API to make NV-CLIP compatible with Ollama's API format"""
    # Handle image processing if provided
    image_embedding = None
    if image:
        image_data = await image.read()
        try:
            image_embedding = process_image(image_data)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process image: {str(e)}"}
            )
    
    # Format prompt with image embedding if available
    formatted_prompt = prompt
    if image_embedding:
        # In a real implementation, you would use the embedding with the prompt
        formatted_prompt = f"[Image analysis] {prompt}"
    
    # Call NV-CLIP's text analysis endpoint with the formatted prompt
    try:
        response = requests.post(
            f"{NVCLIP_URL}/v1/analyze",
            json={
                "text": formatted_prompt,
                "image_embedding": image_embedding["embeddings"][0] if image_embedding else None
            }
        )
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"NV-CLIP API error: {response.text}"}
            )
            
        # Convert NV-CLIP response to Ollama format
        nvclip_response = response.json()
        
        return {
            "model": "nvclip",
            "created_at": nvclip_response.get("created_at", ""),
            "response": nvclip_response.get("analysis", "No analysis provided"),
            "done": True
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process request: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info")