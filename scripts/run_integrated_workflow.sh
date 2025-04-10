#!/bin/bash
# scripts/run_integrated_workflow.sh

# Set environment variables
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=training_data
export WEAVIATE_URL=http://weaviate:8080

echo "Starting integrated AI workflow..."

# Step 1: Data Storage and Processing
echo "Step 1: Starting data storage and processing services..."
docker-compose -f docker-compose.data-pipeline.yml up -d postgres weaviate rapids-processing
echo "Waiting for databases to initialize..."
sleep 30  # Wait for databases to be ready

# Step 2: Run Data Pipeline
echo "Step 2: Running data pipeline..."
docker-compose -f docker-compose.data-pipeline.yml up data-pipeline
echo "Data pipeline completed!"

# Step 3: Fine-Tuning
echo "Step 3: Starting model fine-tuning..."
docker-compose -f docker-compose.training.yml up
echo "Fine-tuning completed!"

# Step 4: Model Conversion
echo "Step 4: Converting model to optimized format..."
docker-compose -f docker-compose.conversion.yml up
echo "Model conversion completed!"

# Step 5: Registration with Ollama
echo "Step 5: Registering model with Ollama..."
docker-compose -f docker-compose.registration.yml up
echo "Model registered with Ollama!"

# Step 6: Deployment to Triton
echo "Step 6: Deploying inference server..."
docker-compose -f docker-compose.inference.yml up -d
echo "Inference server deployed!"

# Step 7: Start API Gateway
echo "Step 7: Starting API Gateway..."
docker-compose -f docker-compose.api-gateway.yml up -d
echo "API Gateway started!"

# Step 8: Start Monitoring
echo "Step 8: Starting monitoring services..."
docker-compose -f docker-compose.monitoring.yml up -d
echo "Monitoring deployed!"

echo "Integrated workflow completed successfully!"

# Step 6: Deployment to Triton
echo "Step 6: Deploying inference server..."
docker-compose -f docker-compose.inference.yml up -d
echo "Inference server deployed!"

# Step 7: Start API Gateway
echo "Step 7: Starting API Gateway..."
docker-compose -f docker-compose.api-gateway.yml up -d
echo "API Gateway started!"

# Step 7.5: Starting LLM Router
echo "Step 7.5: Starting LLM Router..."
docker-compose -f docker-compose.llm-router.yml up -d
echo "LLM Router started!"

# Step 8: Start Monitoring
echo "Step 8: Starting monitoring services..."
docker-compose -f docker-compose.monitoring.yml up -d
echo "Monitoring deployed!"