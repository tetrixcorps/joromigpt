# docker/ai-infrastructure/translation-layer/Dockerfile
FROM nvcr.io/nvidia/nemo:23.06

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Install additional dependencies
RUN apt-get update && apt-get install -y curl
RUN pip install fastapi uvicorn pydantic redis prometheus-client python-json-logger

# Create necessary directories
RUN mkdir -p /app/logs /app/configs /app/translation_data

WORKDIR /app

# Copy application code
COPY src/backend/ai/translation /app/translation
COPY src/backend/ai/utils /app/utils
COPY configs/translation /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting Translation Service..."\n\
\n\
# Start the service\n\
python -m translation.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Expose port for API
EXPOSE 8003

ENTRYPOINT ["/app/entrypoint.sh"]