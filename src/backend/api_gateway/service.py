# src/backend/api_gateway/service.py (update)
LLM_ROUTER_ENDPOINT = os.getenv("LLM_ROUTER_ENDPOINT", "http://llm-router:6060")

@app.post("/v1/completions")
async def completions(request: Request):
    """Route to the appropriate LLM based on complexity"""
    return await proxy_request(f"{LLM_ROUTER_ENDPOINT}/v1/chat/completions", request)