# /src/backend/tests/integration/test_llm_service.py
import pytest
import httpx
import json
from src.backend.utils.llm_client import query_llm

@pytest.mark.integration
async def test_llm_service_integration():
    """Test the integration with the LLM service"""
    # This test requires the LLM service to be running
    try:
        # Use httpx for async HTTP requests
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5000/generate",
                json={
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7,
                    "router": "mf",
                    "threshold": 0.11593
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "generated_text" in data
            assert isinstance(data["generated_text"], str)
            assert len(data["generated_text"]) > 0
    except httpx.ConnectError:
        pytest.skip("LLM service is not running")