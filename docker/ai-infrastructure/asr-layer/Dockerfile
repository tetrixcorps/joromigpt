# docker/ai-infrastructure/asr-layer/Dockerfile
FROM nvcr.io/nvidia/riva/riva-speech:2.11.0-server

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Install additional dependencies
RUN apt-get update && apt-get install -y python3-pip curl
RUN pip install fastapi uvicorn pydantic redis prometheus-client python-json-logger

# Create necessary directories
RUN mkdir -p /app/logs /app/configs /app/data

WORKDIR /app

# Copy application code
COPY src/backend/ai/asr /app/asr
COPY src/backend/ai/utils /app/utils
COPY configs/asr /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting ASR Service..."\n\
\n\
# Start the service\n\
python -m asr.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port for API
EXPOSE 8001

ENTRYPOINT ["/app/entrypoint.sh"]