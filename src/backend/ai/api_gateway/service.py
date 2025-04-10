# src/backend/api_gateway/service.py
import os
import logging
from fastapi import FastAPI, HTTPException, Request
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Infrastructure API Gateway")

# Service endpoints
INFERENCE_ENDPOINT = os.getenv("INFERENCE_ENDPOINT", "http://triton-server:8000")
TRAINING_ENDPOINT = os.getenv("TRAINING_ENDPOINT", "http://pytorch-training:7000")
DATA_PROCESSING_ENDPOINT = os.getenv("DATA_PROCESSING_ENDPOINT", "http://rapids-processing:7500")
ASR_ENDPOINT = os.getenv("ASR_ENDPOINT", "http://riva-asr:8001")
TTS_ENDPOINT = os.getenv("TTS_ENDPOINT", "http://riva-tts:8002")
LLM_ROUTER_ENDPOINT = os.getenv("LLM_ROUTER_ENDPOINT", "http://llm-router:6060")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/inference/{path:path}")
async def inference_proxy(path: str, request: Request):
    """Proxy requests to inference service"""
    return await proxy_request(f"{INFERENCE_ENDPOINT}/{path}", request)

@app.post("/training/{path:path}")
async def training_proxy(path: str, request: Request):
    """Proxy requests to training service"""
    return await proxy_request(f"{TRAINING_ENDPOINT}/{path}", request)

@app.post("/data/{path:path}")
async def data_proxy(path: str, request: Request):
    """Proxy requests to data processing service"""
    return await proxy_request(f"{DATA_PROCESSING_ENDPOINT}/{path}", request)

@app.post("/asr/{path:path}")
async def asr_proxy(path: str, request: Request):
    """Proxy requests to ASR service"""
    return await proxy_request(f"{ASR_ENDPOINT}/{path}", request)

@app.post("/tts/{path:path}")
async def tts_proxy(path: str, request: Request):
    """Proxy requests to TTS service"""
    return await proxy_request(f"{TTS_ENDPOINT}/{path}", request)

@app.post("/v1/completions")
async def completions(request: Request):
    """Route to the appropriate LLM based on complexity"""
    return await proxy_request(f"{LLM_ROUTER_ENDPOINT}/v1/chat/completions", request)

async def proxy_request(url: str, request: Request):
    """Proxy a request to a service"""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        # Remove headers that might cause issues
        headers.pop("host", None)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params,
                timeout=60.0
            )
            
            return response.json()
    except Exception as e:
        logger.error(f"Error proxying request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))