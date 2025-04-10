# /src/backend/tests/unit/test_llm_client.py
import pytest
import json
from unittest.mock import patch, MagicMock
from src.backend.utils.llm_client import query_llm

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {
        "generated_text": "Quantum computing is like regular computing but with qubits instead of bits.",
        "model_used": "test-model",
        "tokens_generated": 15
    }
    return mock

def test_query_llm_parameters():
    """Test that query_llm constructs the correct payload with default parameters"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {}
        
        query_llm("Test prompt")
        
        # Check that the request was made with the correct parameters
        args, kwargs = mock_post.call_args
        assert args[0] == "http://localhost:5000/generate"
        assert kwargs['json']['messages'][0]['content'] == "Test prompt"
        assert kwargs['json']['max_tokens'] == 500
        assert kwargs['json']['temperature'] == 0.7
        assert kwargs['json']['router'] == "mf"
        assert kwargs['json']['threshold'] == 0.11593

def test_query_llm_custom_parameters():
    """Test that query_llm respects custom parameters"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {}
        
        query_llm(
            "Test prompt", 
            max_tokens=100, 
            temperature=0.5, 
            router="custom", 
            threshold=0.2
        )
        
        # Check that the request was made with the custom parameters
        args, kwargs = mock_post.call_args
        assert kwargs['json']['max_tokens'] == 100
        assert kwargs['json']['temperature'] == 0.5
        assert kwargs['json']['router'] == "custom"
        assert kwargs['json']['threshold'] == 0.2

def test_query_llm_response_handling(mock_response):
    """Test that query_llm correctly handles the response"""
    with patch('requests.post', return_value=mock_response):
        result = query_llm("Test prompt")
        
        assert "generated_text" in result
        assert result["model_used"] == "test-model"
        assert result["tokens_generated"] == 15