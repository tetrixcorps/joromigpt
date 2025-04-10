# src/backend/ai/utils/rapids_client.py
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class RapidsClient:
    def __init__(self, base_url: str = "http://rapids-processing:7500"):
        self.base_url = base_url
    
    def process_data(self, data: List[Dict[str, Any]], operations: List[str], output_format: str = "json"):
        """Process data using RAPIDS service."""
        try:
            response = requests.post(
                f"{self.base_url}/process",
                json={
                    "data": data,
                    "operations": operations,
                    "output_format": output_format
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error processing data with RAPIDS: {str(e)}")
            raise
    
    def analyze_dataset(self, dataset_path: str, analysis_type: str):
        """Analyze dataset using RAPIDS service."""
        try:
            response = requests.post(
                f"{self.base_url}/analyze",
                json={
                    "dataset_path": dataset_path,
                    "analysis_type": analysis_type
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error analyzing dataset with RAPIDS: {str(e)}")
            raise
    
    def prepare_for_llm(self, data_path: str):
        """Prepare data for LLM consumption."""
        try:
            response = requests.post(
                f"{self.base_url}/prepare-for-llm",
                params={"data_path": data_path}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error preparing data for LLM: {str(e)}")
            raise