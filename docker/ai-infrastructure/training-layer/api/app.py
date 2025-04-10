# docker/ai-infrastructure/training-layer/api/app.py
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
import subprocess
import os
import logging

app = FastAPI(title="Training Layer API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingConfig(BaseModel):
    model_name: str = "meta/llama-3-8b"
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 5e-5
    training_data_path: str = "/data/conversations.jsonl"

@app.post("/train")
async def train_model(config: TrainingConfig, background_tasks: BackgroundTasks):
    """Start an asynchronous training job with the specified configuration"""
    logger.info(f"Starting training with config: {config.dict()}")
    
    background_tasks.add_task(
        run_training_job,
        config.model_name,
        config.epochs,
        config.batch_size,
        config.learning_rate,
        config.training_data_path
    )
    
    return {"status": "Training job started", "config": config.dict()}

def run_training_job(model_name, epochs, batch_size, learning_rate, training_data_path):
    """Execute the training job in the model-utils container"""
    try:
        cmd = [
            "docker", "exec", "training-model-utils",
            "python", "/opt/nvidia/model-utils/train.py",
            "--model", model_name,
            "--epochs", str(epochs),
            "--batch-size", str(batch_size),
            "--learning-rate", str(learning_rate),
            "--data", training_data_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Training completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Training failed: {e.stderr}")

@app.get("/models")
async def list_models():
    """List all available trained models"""
    models_dir = "/models"
    try:
        models = os.listdir(models_dir)
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return {"error": str(e)}