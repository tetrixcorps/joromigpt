FROM nvcr.io/nim/meta/llama-3.2-3b-instruct:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_CACHE_DIR=/app/model_cache
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Fix permissions and install pip
RUN mkdir -p /var/lib/apt/lists/partial && \
    chmod 755 /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y python3-pip

# Install additional Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.23.2 \
    prometheus-client==0.17.1 \
    python-json-logger==2.0.7 \
    pydantic==2.4.2 \
    redis==5.0.1

# Create necessary directories
RUN mkdir -p /app/model_cache \
    /app/logs \
    /app/configs

WORKDIR /app

# Copy application code
COPY src/backend/ai/models/answer_generation /app/answer_generation
COPY src/backend/ai/utils /app/utils
COPY configs/answer_generation /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
export MODEL_ID="llama-3.2-3b-instruct"\n\
\n\
# Start the service\n\
python -m answer_generation.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports for API and monitoring
EXPOSE 8000
EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]