# src/backend/ai/adapters/custom_llm.py
import requests
import logging
from typing import Any, List, Mapping, Optional
from langchain_core.language_models import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

logger = logging.getLogger(__name__)

class InternalLLMService(LLM):
    """Adapter for internal LLM service."""
    
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.generate_endpoint = f"{base_url}/generate"
    
    @property
    def _llm_type(self) -> str:
        return "internal_llm_service"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the internal LLM service."""
        try:
            payload = {
                "prompt": prompt,
                "stop": stop if stop else [],
                **kwargs
            }
            
            response = requests.post(
                self.generate_endpoint,
                json=payload
            )
            response.raise_for_status()
            return response.json()["generated_text"]
        except Exception as e:
            logger.error(f"Error calling LLM service: {str(e)}")
            raise