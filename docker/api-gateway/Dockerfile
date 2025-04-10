# docker/api-gateway/Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/backend/ai/api_gateway /app/api_gateway
COPY src/backend/utils /app/utils

# Create necessary directories
RUN mkdir -p /app/logs /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting API Gateway Service..."\n\
\n\
# Start the service\n\
uvicorn api_gateway.service:app --host 0.0.0.0 --port 8888\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Expose port for API
EXPOSE 8888

ENTRYPOINT ["/app/entrypoint.sh"]