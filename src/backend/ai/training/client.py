# src/backend/ai/training/client.py
import json
import logging
import aiohttp
from typing import Dict, Optional, List, Any

class TrainingServiceClient:
    """Client for interacting with the Training Layer Service API"""
    
    def __init__(self, base_url: str = "http://training-layer:7000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    async def start_training(self, 
                           model_name: str,
                           training_data_path: str,
                           epochs: int = 3,
                           batch_size: int = 4,
                           learning_rate: float = 5e-5,
                           max_sequence_length: int = 512) -> Dict[str, Any]:
        """
        Start a new training job
        
        Args:
            model_name: Base model to fine-tune
            training_data_path: Path to training data file
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for training
            max_sequence_length: Maximum sequence length for tokenization
            
        Returns:
            Dictionary containing job details including job_id
        """
        config = {
            "model_name": model_name,
            "training_data_path": training_data_path,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "max_sequence_length": max_sequence_length
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/train", json=config) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to start training: {error_text}")
                        return {"error": error_text}
                    
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Error starting training: {str(e)}")
            return {"error": str(e)}
    
    async def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a training job
        
        Args:
            job_id: ID of the training job
            
        Returns:
            Dictionary containing job status details
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/train/{job_id}/status") as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to get training status: {error_text}")
                        return {"error": error_text}
                    
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Error getting training status: {str(e)}")
            return {"error": str(e)}
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available trained models
        
        Returns:
            List of dictionaries containing model details
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models") as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to list models: {error_text}")
                        return []
                    
                    result = await response.json()
                    return result.get("models", [])
        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            return []
    
    async def cancel_training(self, job_id: str) -> bool:
        """
        Cancel a running training job
        
        Args:
            job_id: ID of the training job to cancel
            
        Returns:
            Boolean indicating success
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(f"{self.base_url}/train/{job_id}") as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to cancel training: {error_text}")
                        return False
                    
                    result = await response.json()
                    return result.get("status") == "cancelled"
        except Exception as e:
            self.logger.error(f"Error cancelling training: {str(e)}")
            return False
            
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Get details about a specific trained model
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary containing model details
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/models/{model_id}") as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(f"Failed to get model details: {error_text}")
                        return {"error": error_text}
                    
                    return await response.json()
        except Exception as e:
            self.logger.error(f"Error getting model details: {str(e)}")
            return {"error": str(e)}