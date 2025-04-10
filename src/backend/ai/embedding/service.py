# Add to src/backend/ai/embedding/service.py

@app.post("/embed")
async def embed_texts(request: dict):
    """Endpoint for LangChain adapter to get embeddings"""
    try:
        texts = request.get("texts", [])
        if not texts:
            raise HTTPException(status_code=400, detail="No texts provided")
            
        embeddings = await generate_embeddings(texts)
        return {"embeddings": embeddings}
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))