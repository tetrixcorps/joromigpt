# scripts/setup_triton_model.py
import os
import json

# Create Triton model repository structure
os.makedirs("/model_repository/ollama_model/1", exist_ok=True)

# Create config.pbtxt
config = """
name: "ollama_model"
platform: "ensemble"
max_batch_size: 8
input [
  {
    name: "TEXT"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }
]
output [
  {
    name: "GENERATED_TEXT"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }
]
ensemble_scheduling {
  step [
    {
      model_name: "text_generation"
      model_version: -1
      input_map {
        key: "prompt"
        value: "TEXT"
      }
      output_map {
        key: "text"
        value: "GENERATED_TEXT"
      }
    }
  ]
}
"""

with open("/model_repository/ollama_model/config.pbtxt", "w") as f:
    f.write(config)

# Create Python backend for Ollama integration
os.makedirs("/model_repository/text_generation/1", exist_ok=True)

ollama_backend = """
import json
import numpy as np
import requests
import triton_python_backend_utils as pb_utils

class TritonPythonModel:
    def initialize(self, args):
        self.model_name = "custom-domain-model"
        self.ollama_url = "http://host.docker.internal:11434/api/generate"
        
    def execute(self, requests):
        responses = []
        for request in requests:
            input_text = pb_utils.get_input_tensor_by_name(request, "prompt").as_numpy()[0].decode('utf-8')
            
            # Call Ollama API
            response = requests.post(
                self.ollama_url,
                json={"model": self.model_name, "prompt": input_text}
            )
            
            if response.status_code == 200:
                output_text = response.json().get("response", "")
            else:
                output_text = f"Error: {response.text}"
                
            # Create output tensor
            output_tensor = pb_utils.Tensor("text", np.array([output_text.encode('utf-8')], dtype=np.object_))
            response = pb_utils.InferenceResponse(output_tensors=[output_tensor])
            responses.append(response)
            
        return responses
"""

with open("/model_repository/text_generation/1/model.py", "w") as f:
    f.write(ollama_backend)

# Create config.pbtxt for Python backend
text_gen_config = """
name: "text_generation"
backend: "python"
max_batch_size: 8
input [
  {
    name: "prompt"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }
]
output [
  {
    name: "text"
    data_type: TYPE_STRING
    dims: [ -1 ]
  }
]
"""

with open("/model_repository/text_generation/config.pbtxt", "w") as f:
    f.write(text_gen_config)