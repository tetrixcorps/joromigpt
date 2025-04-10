# /src/backend/tests/unit/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from src.backend.main import app

client = TestClient(app)

def test_tts_synthesize_endpoint():
    """Test the text-to-speech synthesis endpoint"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audio_url": "https://example.com/audio.mp3",
            "duration": 2.5
        }
        mock_post.return_value = mock_response
        
        response = client.post(
            "/tts/synthesize",
            data={
                "text": "Hello world",
                "language": "en-US",
                "voice": "female-1",
                "speaking_rate": 1.0,
                "pitch": 0.0
            }
        )
        
        assert response.status_code == 200
        assert "audio_url" in response.json()
        assert "duration" in response.json()

def test_tts_synthesize_error_handling():
    """Test error handling in the TTS endpoint"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response
        
        response = client.post(
            "/tts/synthesize",
            data={
                "text": "Hello world",
                "language": "en-US",
                "voice": "female-1",
                "speaking_rate": 1.0,
                "pitch": 0.0
            }
        )
        
        assert response.status_code == 500
        assert "detail" in response.json()