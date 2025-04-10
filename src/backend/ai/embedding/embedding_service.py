from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()
NIM_ENDPOINT = "http://localhost:8000/v1/embeddings"

@app.post("/embed")
async def embed_data(text: str = None, image: UploadFile = File(None)):
    if image:
        image_data = await image.read()
    else:
        image_data = None

    payload = {
        "input": text or image_data,
        "model": "nv-clip-vit-h",
        "encoding_format": "float"
    }
    
    response = requests.post(NIM_ENDPOINT, json=payload)
    return response.json()

@app.post("/embed/batch")
async def embed_batch_data(inputs: list):
    payload = {
        "input": inputs,
        "model": "nv-clip-vit-h",
        "encoding_format": "float"
    }
    
    response = requests.post(NIM_ENDPOINT, json=payload)
    return response.json()