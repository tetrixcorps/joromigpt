#!/bin/bash

# Create root project directory
mkdir -p JOROMIGPT

# Create main project structure
cd JOROMIGPT

# Create GitHub workflows directory
mkdir -p .github/workflows

# Create docker configuration directories with AI infrastructure layers
mkdir -p docker/{api-gateway,frontend,worker,riva,triton,monitoring}/
mkdir -p docker/ai-infrastructure/{web-layer,llm-layer,mcp-layer,training-layer,k8s-layer,hpc-layer,cuda-layer,nvidia-toolkit-layer,host-driver-layer}

# Create source code directories
mkdir -p src/{frontend,backend}

# Create backend structure
mkdir -p src/backend/{api,core,services,utils,workers}
mkdir -p src/backend/tests

# Create AI model layers
mkdir -p src/backend/ai/{llm,training,inference}
mkdir -p src/backend/ai/models/{base,fine-tuned}
mkdir -p src/backend/ai/optimizers
mkdir -p src/backend/ai/pipelines

# Create frontend structure
mkdir -p src/frontend/{public,src}
mkdir -p src/frontend/src/{components,services,utils}

# Create configuration directories
mkdir -p config/{dev,staging,prod}
mkdir -p config/ai/{llm,training,inference}

# Create model directories
mkdir -p models/{asr,tts,translation,llm}
mkdir -p models/training/{checkpoints,artifacts}

# Create scripts directory with AI-specific scripts
mkdir -p scripts/{deployment,monitoring,ai-ops}

# Create monitoring directory
mkdir -p monitoring/{prometheus,grafana}

# Create necessary files
touch docker-compose.yml
touch docker-compose.dev.yml
touch docker-compose.staging.yml
touch docker-compose.prod.yml
touch .env.example
touch README.md

# Create Docker-related files
touch docker/api-gateway/{Dockerfile,requirements.txt}
touch docker/frontend/{Dockerfile,nginx.conf}
touch docker/worker/{Dockerfile,requirements.txt}
touch docker/monitoring/{Dockerfile,prometheus.yml}

# Create AI infrastructure layer configurations
touch docker/ai-infrastructure/llm-layer/Dockerfile
touch docker/ai-infrastructure/training-layer/Dockerfile
touch docker/ai-infrastructure/cuda-layer/cuda.conf
touch docker/ai-infrastructure/nvidia-toolkit-layer/toolkit.conf

# Create basic backend files
touch src/backend/main.py
touch src/backend/requirements.txt

# Create AI service files
touch src/backend/ai/llm/service.py
touch src/backend/ai/training/trainer.py
touch src/backend/ai/inference/predictor.py

# Create basic frontend files
touch src/frontend/package.json
touch src/frontend/tsconfig.json

# Create GitHub Actions workflows
touch .github/workflows/ci.yml
touch .github/workflows/deploy.yml

# Create AI-specific workflow
touch .github/workflows/ai-training.yml

# Create data directories for Docker
mkdir -p data/{bionemo,riva,nvclip,triton-tensorrt,triton-vllm,llama,pytorch,snowflake}
mkdir -p data/{cuda,rapids,merlin,content-safety}
mkdir -p data/tao/{data,models,results}

# Create config directories for Docker
mkdir -p config/{kafka,k8s,deepstream}

# Create notebooks directory for TensorFlow
mkdir -p notebooks

# Create dummy scripts for deployment and ai-ops
touch scripts/deployment/deploy.sh
touch scripts/ai-ops/ai_ops.sh

# Make scripts executable
chmod +x scripts/deployment/*.sh
chmod +x scripts/ai-ops/*.sh

echo "Project structure with AI infrastructure created successfully!"
echo "Run 'docker-compose up -d' to start all services"