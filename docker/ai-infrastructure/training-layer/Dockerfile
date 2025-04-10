# docker/ai-infrastructure/training-layer/Dockerfile
FROM nvcr.io/eevaigoeixww/conversational-ai/model-utils:4.0.0

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV MODEL_CACHE_DIR=/app/model_cache
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV NVIDIA_VISIBLE_DEVICES=all

# Install additional dependencies
RUN apt-get update && apt-get install -y curl python3-pip
RUN pip3 install --no-cache-dir --upgrade pip

# Install PyTorch with CUDA support
RUN pip3 install --no-cache-dir torch==2.1.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html

# Install transformers, datasets, and other requirements
RUN pip3 install --no-cache-dir \
    transformers==4.36.0 \
    datasets==2.15.0 \
    peft==0.7.0 \
    accelerate==0.25.0 \
    bitsandbytes==0.41.0 \
    fastapi==0.104.1 \
    uvicorn==0.23.2 \
    pydantic==2.4.2 \
    redis==5.0.1 \
    prometheus-client==0.17.1 \
    python-json-logger==2.0.7

# Create necessary directories
RUN mkdir -p /app/model_cache \
    /app/data \
    /app/checkpoints \
    /app/logs \
    /app/configs

WORKDIR /app

# Copy application code
COPY src/backend/ai/training /app/training
COPY src/backend/ai/utils /app/utils
COPY configs/training /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting Training Service..."\n\
\n\
# Start the service\n\
python -m uvicorn training.service:app --host 0.0.0.0 --port 7000\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7000/health || exit 1

# Expose port for API
EXPOSE 7000

ENTRYPOINT ["/app/entrypoint.sh"]