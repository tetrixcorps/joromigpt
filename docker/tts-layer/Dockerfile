# docker/ai-infrastructure/tts-layer/Dockerfile
FROM nvcr.io/nvidia/riva/riva-speech:2.11.0-server

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Install additional dependencies
RUN apt-get update && apt-get install -y python3-pip curl
RUN pip install fastapi uvicorn pydantic redis prometheus-client python-json-logger

# Create necessary directories
RUN mkdir -p /app/logs /app/configs /app/tts_data

WORKDIR /app

# Copy application code
COPY src/backend/ai/tts /app/tts
COPY src/backend/ai/utils /app/utils
COPY configs/tts /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting TTS Service..."\n\
\n\
# Start the service\n\
python -m tts.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port for API
EXPOSE 8002

ENTRYPOINT ["/app/entrypoint.sh"]