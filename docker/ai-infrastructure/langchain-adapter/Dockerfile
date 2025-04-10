# docker/ai-infrastructure/langchain-adapter/Dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LANGCHAIN_TRACING_V2=true
ENV LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# Install dependencies
RUN apt-get update && apt-get install -y curl build-essential git
RUN pip install --no-cache-dir langchain==0.1.8 \
    langchain-community==0.0.19 \
    langchain-core==0.1.17 \
    langchain-weaviate==0.0.2 \
    fastapi==0.109.2 \
    uvicorn==0.27.0 \
    pydantic==2.5.3 \
    redis==5.0.1 \
    prometheus-client==0.19.0 \
    python-dotenv==1.0.0 \
    python-json-logger==2.0.7 \
    weaviate-client==3.26.2

# Create necessary directories
RUN mkdir -p /app/logs /app/configs /app/data

WORKDIR /app

# Copy application code
COPY src/backend/ai/adapters /app/adapters
COPY src/backend/ai/utils /app/utils
COPY configs/langchain /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting LangChain Adapter Service..."\n\
\n\
# Start the service\n\
python -m adapters.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7100/health || exit 1

# Expose port for API
EXPOSE 7100

ENTRYPOINT ["/app/entrypoint.sh"]