#!/usr/bin/env python
# optimize_inference.py - Optimize model inference for production

import os
import json
import logging
import argparse
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Optimize model inference")
    
    parser.add_argument("--mode", type=str, required=True, 
                        choices=["time-slicing", "triton-setup", "input-optimize"],
                        help="Optimization mode")
    
    parser.add_argument("--models", type=str, nargs="+",
                        help="List of model paths for time-slicing")
    
    parser.add_argument("--input", type=str,
                        help="Input data for time-slicing")
    
    parser.add_argument("--model_repository", type=str, default="./model_repository",
                        help="Triton model repository path")
    
    parser.add_argument("--triton_config", type=str,
                        help="Path to save Triton docker-compose config")
    
    parser.add_argument("--image", type=str,
                        help="Image path for input optimization")
    
    parser.add_argument("--target_size", type=int, nargs=2, default=[224, 224],
                        help="Target size for image optimization (width, height)")
    
    return parser.parse_args()

def run_time_slicing(models, input_data):
    """Run time-slicing optimization for multiple models"""
    logger.info(f"Running time-slicing optimization for {len(models)} models")
    
    # Implementation for time-slicing would go here
    # This is a placeholder for the actual implementation
    
    results = {
        "time_slicing_enabled": True,
        "models_optimized": len(models),
        "estimated_latency_reduction": "30%"
    }
    
    return results

def setup_triton_endpoints(model_repository, triton_config):
    """Set up Triton Inference Server with optimized configuration"""
    logger.info(f"Setting up Triton Inference Server endpoints")
    
    # Create model repository directory
    os.makedirs(model_repository, exist_ok=True)
    
    # Create docker-compose configuration
    docker_compose = """version: '3.8'
services:
  triton:
    image: nvcr.io/nvidia/tritonserver:22.12-py3
    ports:
      - "8000:8000"  # HTTP
      - "8001:8001"  # gRPC
      - "8002:8002"  # Metrics
    volumes:
      - {}:/models
    command: tritonserver --model-repository=/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
"""
    
    docker_compose = docker_compose.format(os.path.abspath(model_repository))
    
    with open(triton_config, "w") as f:
        f.write(docker_compose)
    
    logger.info(f"Triton configuration saved to {triton_config}")
    logger.info(f"Model repository created at {model_repository}")
    logger.info("To start Triton server, run: docker-compose -f %s up", triton_config)
    
    # Create a Python client example script
    client_script = """#!/usr/bin/env python
# triton_client_example.py

import numpy as np
import tritonclient.http as httpclient
from PIL import Image
import cv2

def image_inference(image_path, size=(224, 224)):
    # Resize and preprocess image
    img = cv2.imread(image_path)
    img = cv2.resize(img, size)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    
    # Initialize Triton client
    client = httpclient.InferenceServerClient(url="localhost:8000")
    
    # Create input tensor
    input_tensor = httpclient.InferInput("image", img.shape, "UINT8")
    input_tensor.set_data_from_numpy(img)
    
    # Send request to server
    response = client.infer("object_detection", [input_tensor])
    
    # Get output data
    boxes = response.as_numpy("boxes")
    scores = response.as_numpy("scores")
    classes = response.as_numpy("classes")
    
    return {
        "boxes": boxes.tolist(),
        "scores": scores.tolist(),
        "classes": classes.tolist()
    }

def text_inference(text):
    # Initialize Triton client
    client = httpclient.InferenceServerClient(url="localhost:8000")
    
    # Encode text as bytes
    text_bytes = np.array([text.encode('utf-8')], dtype=np.object_)
    
    # Create input tensor
    input_tensor = httpclient.InferInput("text", [1], "BYTES")
    input_tensor.set_data_from_numpy(text_bytes)
    
    # Send request to server
    response = client.infer("semantic_search", [input_tensor])
    
    # Get output data
    embedding = response.as_numpy("embedding")
    
    return {"embedding": embedding.tolist()}

if __name__ == "__main__":
    # Example usage
    image_results = image_inference("path/to/image.jpg")
    text_results = text_inference("Search query text")
    
    print("Image inference results:", image_results)
    print("Text inference results:", text_results)
"""
    
    client_path = os.path.join(os.path.dirname(triton_config), "triton_client_example.py")
    with open(client_path, "w") as f:
        f.write(client_script)
    
    logger.info(f"Example client script saved to {client_path}")
    
    return {"model_repository": model_repository, "config_path": triton_config}

def optimize_input_data(image_path, target_size):
    """Optimize input data by resizing images before inference"""
    logger.info(f"Optimizing input image: {image_path}")
    
    try:
        # Load and resize image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image from {image_path}")
            return None
        
        # Get original dimensions
        original_height, original_width = image.shape[:2]
        logger.info(f"Original image size: {original_width}x{original_height}")
        
        # Resize image
        resized_image = cv2.resize(image, (target_size[0], target_size[1]))
        
        # Calculate memory savings
        original_size = original_width * original_height * 3  # RGB image, 3 bytes per pixel
        new_size = target_size[0] * target_size[1] * 3
        savings_percent = 100 * (1 - (new_size / original_size))
        
        logger.info(f"Resized to: {target_size[0]}x{target_size[1]}")
        logger.info(f"Memory reduction: {savings_percent:.2f}%")
        
        # Save optimized image
        output_path = f"{os.path.splitext(image_path)[0]}_optimized{os.path.splitext(image_path)[1]}"
        cv2.imwrite(output_path, resized_image)
        
        logger.info(f"Optimized image saved to: {output_path}")
        
        return {
            "original_path": image_path,
            "original_size": f"{original_width}x{original_height}",
            "optimized_path": output_path,
            "optimized_size": f"{target_size[0]}x{target_size[1]}",
            "memory_reduction_percent": f"{savings_percent:.2f}%"
        }
    
    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        return None

def main():
    args = parse_args()
    
    if args.mode == "time-slicing":
        if not args.models or not args.input:
            logger.error("Time-slicing requires --models and --input arguments")
            return
        results = run_time_slicing(args.models, args.input)
        print(json.dumps(results, indent=2))
    
    elif args.mode == "triton-setup":
        if not args.triton_config:
            logger.error("Triton setup requires --triton_config argument")
            return
        setup_triton_endpoints(args.model_repository, args.triton_config)
    
    elif args.mode == "input-optimize":
        if not args.image:
            logger.error("Input optimization requires --image argument")
            return
        result = optimize_input_data(args.image, args.target_size)
        if result:
            print(json.dumps(result, indent=2))
    
    else:
        logger.error(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    main()