# src/backend/ai/training/trainer.py
import os
import logging
import json
import torch
import time
from datetime import datetime
from pathlib import Path
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
import redis
from datasets import Dataset

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class ModelTrainer:
    def __init__(self, model_name, output_dir="/app/checkpoints", device=None):
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        
    def prepare_model(self):
        """Load base model and tokenizer"""
        logger.info(f"Loading model {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
        )
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        return self.model, self.tokenizer
        
    def load_dataset(self, data_path):
        """Load and preprocess conversation dataset"""
        with open(data_path, 'r') as f:
            data = [json.loads(line) for line in f]
            
        # Format data for training
        formatted_data = []
        for item in data:
            if "conversations" in item:
                text = ""
                for turn in item["conversations"]:
                    role = turn.get("role", "user")
                    content = turn.get("content", "")
                    if role == "user":
                        text += f"USER: {content}\n"
                    else:
                        text += f"ASSISTANT: {content}\n"
                formatted_data.append({"text": text})
                
        return Dataset.from_list(formatted_data)
        
    def train(self, dataset, job_id, config):
        """Fine-tune the model with LoRA"""
        # Configure LoRA
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,  # rank
            lora_alpha=32,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        )
        
        # Apply LoRA config
        model = get_peft_model(self.model, peft_config)
        
        # Tokenize dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"], 
                padding="max_length", 
                truncation=True, 
                max_length=config.max_sequence_length
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Define training arguments
        training_args = TrainingArguments(
            output_dir=f"{self.output_dir}/{job_id}",
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            gradient_accumulation_steps=4,
            learning_rate=config.learning_rate,
            weight_decay=0.01,
            warmup_steps=config.warmup_steps,
            logging_steps=10,
            evaluation_strategy=config.evaluation_strategy,
            eval_steps=config.eval_steps,
            save_steps=config.save_steps,
            fp16=self.device == "cuda",
            report_to="none",
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer, mlm=False
            ),
        )
        
        # Training progress callback
        class ProgressCallback:
            def __init__(self, job_id):
                self.job_id = job_id
                
            def on_log(self, args, state, control, logs=None, **kwargs):
                logs = logs or {}
                
                # Get training status from Redis
                status_str = redis_client.get(f"training_status:{self.job_id}")
                if not status_str:
                    return
                    
                status = json.loads(status_str)
                
                # Update training metrics
                step = state.global_step
                loss = logs.get("loss", 0)
                
                if "epoch" in logs:
                    status["current_epoch"] = logs["epoch"]
                    
                # Update progress
                total_steps = state.max_steps
                status["current_step"] = step
                status["progress"] = min(step / total_steps if total_steps > 0 else 0, 0.99)
                status["loss"] = loss
                status["last_update"] = datetime.now().isoformat()
                
                # Store updated status
                redis_client.set(f"training_status:{self.job_id}", json.dumps(status))
        
        # Add callback
        trainer.add_callback(ProgressCallback(job_id))
        
        # Train model
        trainer.train()
        
        # Save model
        model_path = f"{self.output_dir}/{job_id}/final"
        trainer.save_model(model_path)
        self.tokenizer.save_pretrained(model_path)
        
        return model_path

def store_training_status(job_id, status):
    """Store training job status in Redis"""
    try:
        if isinstance(status, dict):
            status_json = json.dumps(status)
        else:
            # Convert Pydantic model to dict then to JSON
            status_json = json.dumps(status.dict())
            
        redis_client.set(f"training_status:{job_id}", status_json)
        return True
    except Exception as e:
        logger.error(f"Failed to store training status: {str(e)}")
        return False

def get_stored_training_status(job_id):
    """Retrieve training job status from Redis"""
    try:
        status_json = redis_client.get(f"training_status:{job_id}")
        if not status_json:
            return None
        return json.loads(status_json)
    except Exception as e:
        logger.error(f"Failed to get training status: {str(e)}")
        return None

def list_available_models():
    """List all available trained models"""
    try:
        model_dir = "/app/checkpoints"
        models = []
        
        if not os.path.exists(model_dir):
            return []
            
        for item in os.listdir(model_dir):
            item_path = os.path.join(model_dir, item)
            if os.path.isdir(item_path):
                # Check if this is a complete model (has a final folder)
                final_path = os.path.join(item_path, "final")
                is_complete = os.path.exists(final_path)
                
                # Get creation time
                created_time = datetime.fromtimestamp(
                    os.path.getctime(item_path)
                ).isoformat()
                
                models.append({
                    "id": item,
                    "name": item,
                    "status": "completed" if is_complete else "in_progress",
                    "created": created_time
                })
                
        return models
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        return []

def cancel_training_job(job_id):
    """Cancel a running training job"""
    try:
        status = get_stored_training_status(job_id)
        if not status:
            return False
            
        status["status"] = "cancelled"
        status["end_time"] = datetime.now().isoformat()
        store_training_status(job_id, status)
        
        # Could implement actual process termination here
        # depending on how training is run
        
        return True
    except Exception as e:
        logger.error(f"Failed to cancel training job: {str(e)}")
        return False

def run_training_job(job_id, config):
    """Execute the complete training job pipeline"""
    try:
        # Update status to running
        status = get_stored_training_status(job_id)
        if not status:
            logger.error(f"No status found for job {job_id}")
            return
            
        status["status"] = "running"
        store_training_status(job_id, status)
        
        # Initialize trainer
        trainer = ModelTrainer(
            model_name=config.model_name,
            output_dir=config.output_dir
        )
        
        # Prepare model and tokenizer
        trainer.prepare_model()
        
        # Load dataset
        dataset = trainer.load_dataset(config.training_data_path)
        
        # Train model
        model_path = trainer.train(dataset, job_id, config)
        
        # Update status to completed
        status = get_stored_training_status(job_id)
        status["status"] = "completed"
        status["progress"] = 1.0
        status["end_time"] = datetime.now().isoformat()
        status["model_path"] = model_path
        store_training_status(job_id, status)
        
        logger.info(f"Training completed for job {job_id}. Model saved to {model_path}")
        
        # Add model conversion to GGUF if needed
        # convert_to_gguf(model_path)
        
        return model_path
        
    except Exception as e:
        logger.error(f"Training failed for job {job_id}: {str(e)}")
        
        # Update status to failed
        status = get_stored_training_status(job_id)
        if status:
            status["status"] = "failed"
            status["error"] = str(e)
            status["end_time"] = datetime.now().isoformat()
            store_training_status(job_id, status)