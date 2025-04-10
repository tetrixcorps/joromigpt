# /src/backend/tests/security/test_api_security.py
import requests
import json
import time

def test_rate_limiting():
    """Test if the API has rate limiting protection"""
    endpoint = "http://localhost:8000/llm/chat"
    
    # Send multiple requests in quick succession
    start_time = time.time()
    responses = []
    
    for i in range(20):
        response = requests.post(
            endpoint,
            json={
                "messages": [
                    {"role": "user", "content": f"Test message {i}"}
                ],
                "max_tokens": 10,
                "temperature": 0.7
            }
        )
        responses.append(response)
    
    end_time = time.time()
    
    # Check if any responses indicate rate limiting
    rate_limited = any(r.status_code == 429 for r in responses)
    
    # If no rate limiting is detected, print a warning
    if not rate_limited:
        print("WARNING: No rate limiting detected. The API may be vulnerable to DoS attacks.")
    
    # Check response times for signs of throttling
    response_times = [r.elapsed.total_seconds() for r in responses]
    increasing_times = all(response_times[i] <= response_times[i+1] for i in range(len(response_times)-1))
    
    if increasing_times:
        print("Response times are increasing, which may indicate throttling.")
    else:
        print("No signs of throttling detected.")

def test_sql_injection():
    """Test if the API is vulnerable to SQL injection"""
    endpoint = "http://localhost:8000/llm/chat"
    
    # SQL injection payloads
    payloads = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; SELECT * FROM users; --"
    ]
    
    for payload in payloads:
        response = requests.post(
            endpoint,
            json={
                "messages": [
                    {"role": "user", "content": payload}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
        )
        
        # Check if the response contains any SQL error messages
        if response.status_code >= 500:
            print(f"WARNING: Potential SQL injection vulnerability with payload: {payload}")
            print(f"Response: {response.text}")
        
        # Check if the response contains any database information
        if "table" in response.text.lower() or "sql" in response.text.lower():
            print(f"WARNING: Response may contain database information with payload: {payload}")
            print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Running API security tests...")
    test_rate_limiting()
    test_sql_injection()
    print("API security tests completed.")