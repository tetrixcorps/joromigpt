# src/backend/ai/llm/multimodal_router_client.py
import base64
import os
from typing import Optional, Dict, Any, Union
from routellm.controller import Controller

class MultimodalLLMRouter:
    """Router client that supports both text and multimodal inputs"""
    
    def __init__(self):
        self.client = Controller(
            routers=["mf"],  # Use the "mf" (model family) router
            strong_model="gpt-4-vision-preview",  # Strong multimodal model
            weak_model="ollama_chat/nvclip",      # NV-CLIP as weak model through Ollama
        )
        
        # Configure thresholds - may need calibration for your specific use case
        self.text_threshold = 0.11593  # Default threshold for text
        self.image_threshold = 0.05    # Lower threshold for images (prefers strong model)
        
    def generate_response(self, prompt: str, image_path: Optional[str] = None) -> str:
        """
        Generate a response using the appropriate model based on complexity
        Supports both text-only and image+text inputs
        
        Args:
            prompt: Text prompt
            image_path: Optional path to an image file
        
        Returns:
            Response from the chosen model
        """
        # Handle multimodal input
        if image_path and os.path.exists(image_path):
            return self._process_multimodal(prompt, image_path)
        
        # Handle text-only input
        return self._process_text(prompt)
    
    def _process_text(self, prompt: str) -> str:
        """Process text-only input"""
        response = self.client.chat.completions.create(
            model=f"router-mf-{self.text_threshold}",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def _process_multimodal(self, prompt: str, image_path: str) -> str:
        """Process multimodal (text + image) input"""
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Create messages with image content
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        # Route with lower threshold to prefer the stronger model for complex multimodal tasks
        response = self.client.chat.completions.create(
            model=f"router-mf-{self.image_threshold}",
            messages=messages
        )
        
        return response.choices[0].message.content