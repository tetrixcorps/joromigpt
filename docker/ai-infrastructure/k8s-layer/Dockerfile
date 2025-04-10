FROM ubuntu:20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NVIDIA_VISIBLE_DEVICES=all

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3-pip curl apt-transport-https gnupg2 && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && \
    apt-get install -y kubectl

# Create necessary directories
RUN mkdir -p /app/logs /app/configs

WORKDIR /app

# Copy application code
COPY src/backend/ai/k8s /app/k8s
COPY src/backend/ai/utils /app/utils
COPY configs/k8s /app/configs

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Set up environment\n\
echo "Starting Kubernetes Layer..."\n\
\n\
# Start the service\n\
python -m k8s.service\n\
' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose ports for API and monitoring
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
