# src/backend/ai/adapters/custom_embeddings.py
import requests
import logging
from typing import List
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

class InternalEmbeddingService(Embeddings):
    """Adapter for internal embedding service."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.embed_endpoint = f"{base_url}/embed"
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using the internal embedding service."""
        try:
            response = requests.post(
                self.embed_endpoint,
                json={"texts": texts}
            )
            response.raise_for_status()
            return response.json()["embeddings"]
        except Exception as e:
            logger.error(f"Error embedding documents: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query using the internal embedding service."""
        try:
            response = requests.post(
                self.embed_endpoint,
                json={"texts": [text]}
            )
            response.raise_for_status()
            return response.json()["embeddings"][0]
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")