# /src/backend/utils/llm_client.py
import requests
import json

def query_llm(prompt, max_tokens=500, temperature=0.7, router="mf", threshold=0.11593):
    """
    Send a query to the LLM service
    
    Args:
        prompt (str): The user's prompt
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Controls randomness (0.0-1.0)
        router (str): Routing strategy ('mf' for matrix factorization)
        threshold (float): Threshold for routing to stronger model
        
    Returns:
        dict: The JSON response from the LLM service
    """
    endpoint = "http://localhost:5000/generate"
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "router": router,  # Matrix factorization router (recommended)
        "threshold": threshold  # Calibrated threshold for ~50% routing to strong model
    }

    response = requests.post(endpoint, json=payload)
    return response.json()

if __name__ == "__main__":
    # Example usage
    prompt = "Explain quantum computing in simple terms"
    result = query_llm(prompt)
    print(json.dumps(result, indent=2))