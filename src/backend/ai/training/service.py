# src/backend/ai/training/service.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from datetime import datetime
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Training Layer Service")

class TrainingConfig(BaseModel):
    model_name: str
    training_data_path: str
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 5e-5
    max_sequence_length: int = 512
    warmup_steps: int = 100
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    save_steps: int = 1000
    output_dir: str = "/app/checkpoints"

class TrainingResponse(BaseModel):
    job_id: str
    status: str
    start_time: datetime
    config: TrainingConfig

class TrainingStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    current_epoch: int
    current_step: int
    loss: float
    eval_loss: Optional[float]
    start_time: datetime
    last_update: datetime

@app.post("/train", response_model=TrainingResponse)
async def start_training(config: TrainingConfig, background_tasks: BackgroundTasks):
    """Start a new training job"""
    try:
        job_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize training status
        training_status = TrainingStatus(
            job_id=job_id,
            status="initializing",
            progress=0.0,
            current_epoch=0,
            current_step=0,
            loss=0.0,
            start_time=datetime.now(),
            last_update=datetime.now()
        )
        
        # Store training status (implementation needed)
        store_training_status(job_id, training_status)
        
        # Start training in background
        background_tasks.add_task(
            run_training_job,
            job_id=job_id,
            config=config
        )
        
        return TrainingResponse(
            job_id=job_id,
            status="started",
            start_time=datetime.now(),
            config=config
        )
        
    except Exception as e:
        logger.error(f"Failed to start training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/train/{job_id}/status", response_model=TrainingStatus)
async def get_training_status(job_id: str):
    """Get the status of a training job"""
    try:
        status = get_stored_training_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Training job {job_id} not found")
        return status
    except Exception as e:
        logger.error(f"Failed to get training status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List all available trained models"""
    try:
        models = list_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/train/{job_id}")
async def cancel_training(job_id: str):
    """Cancel a running training job"""
    try:
        success = cancel_training_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Training job {job_id} not found")
        return {"status": "cancelled", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to cancel training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        @app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "training-layer"}

@app.get("/models/{model_id}")
async def get_model_details(model_id: str):
    """Get details about a specific model"""
    try:
        models = list_available_models()
        model = next((m for m in models if m["id"] == model_id), None)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
        # Add additional details
        model_path = os.path.join("/app/checkpoints", model_id, "final")
        if os.path.exists(model_path):
            # Get model size
            size_bytes = sum(
                os.path.getsize(os.path.join(root, file)) 
                for root, _, files in os.walk(model_path) 
                for file in files
            )
            model["size_mb"] = round(size_bytes / (1024 * 1024), 2)
            
            # Get metadata if available
            metadata_path = os.path.join(model_path, "training_args.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    model["metadata"] = json.load(f)
                    
        return model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))