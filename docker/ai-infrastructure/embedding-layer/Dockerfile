# docker/ai-infrastructure/embedding-layer/Dockerfile
FROM nvcr.io/nim/nvidia/nvclip:2.0.0

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Install additional dependencies
RUN pip install fastapi uvicorn pydantic redis

# Create necessary directories
RUN mkdir -p /app/logs /app/configs

WORKDIR /app

# Copy application code
COPY src/backend/ai/embedding /app/embedding
COPY src/backend/ai/utils /app/utils

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting Embedding Layer..."\n\
\n\
# Start the service\n\
python -m embedding.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose port for API
EXPOSE 9000

ENTRYPOINT ["/app/entrypoint.sh"]