#!/bin/bash
# run_workflow.sh

# Step 1: Data Processing
docker-compose -f docker-compose.data-pipeline.yml up -d
echo "Data processing started..."
# Wait for data processing to complete
sleep 60

# Step 2: Fine-Tuning
docker-compose -f docker-compose.training.yml up
echo "Fine-tuning completed!"

# Step 3: Model Conversion
docker-compose -f docker-compose.conversion.yml up
echo "Model conversion completed!"

# Step 4: Registration with Ollama
docker-compose -f docker-compose.registration.yml up
echo "Model registered with Ollama!"

# Step 5: Deployment to Triton
docker-compose -f docker-compose.inference.yml up -d
echo "Inference server deployed!"

# Step 6: Start Monitoring
docker-compose -f docker-compose.monitoring.yml up -d
echo "Monitoring deployed!"

echo "Workflow completed successfully!"