#!/usr/bin/env python
# ollama_quantize.py - Model quantization script for Ollama models

import os
import time
import argparse
import torch
import logging
from pathlib import Path
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer, 
    TrainingArguments
)
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Quantize LLMs for Ollama deployment")
    parser.add_argument("--model_id", type=str, required=True, help="HuggingFace model ID")
    parser.add_argument("--output_dir", type=str, default="./quantized_model", help="Output directory")
    parser.add_argument("--quant_method", type=str, choices=["bnb", "aimet"], default="bnb", 
                        help="Quantization method: BitsAndBytes or AIMET")
    parser.add_argument("--bits", type=int, choices=[4, 8], default=4, help="Quantization bits")
    parser.add_argument("--apply_qlora", action="store_true", help="Apply QLoRA fine-tuning")
    parser.add_argument("--dataset_path", type=str, help="Path to fine-tuning dataset")
    parser.add_argument("--max_length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument("--convert_gguf", action="store_true", help="Convert to GGUF format")
    parser.add_argument("--gguf_quant", type=str, default="q4_0", 
                        choices=["q4_0", "q4_k_m", "q5_0", "q5_k_m", "q8_0"], 
                        help="GGUF quantization format")
    return parser.parse_args()

def load_base_model(model_id, max_length):
    """Load model in FP16 for baseline comparison"""
    logger.info(f"Loading base model {model_id} in FP16...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        max_length=max_length
    )
    
    # Analyze base memory usage
    memory_gb = base_model.get_memory_footprint() / 1e9
    logger.info(f"FP16 model memory: {memory_gb:.2f} GB")
    
    return base_model, tokenizer

def quantize_with_bnb(model_id, bits, max_length):
    """Quantize model using BitsAndBytes"""
    logger.info(f"Quantizing {model_id} to INT{bits} using BitsAndBytes...")
    
    # Configure quantization
    quant_config = BitsAndBytesConfig(
        load_in_4bit=bits == 4,
        load_in_8bit=bits == 8,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",  # NormalFloat4 format
        bnb_4bit_use_double_quant=True  # Double quantization for further compression
    )
    
    # Load model with quantization
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto",
        max_length=max_length
    )
    
    # Enable memory optimizations
    model.gradient_checkpointing_enable()
    
    # Verify memory reduction
    memory_gb = model.get_memory_footprint() / 1e9
    logger.info(f"INT{bits} model memory: {memory_gb:.2f} GB")
    
    return model, tokenizer

def quantize_with_aimet(model_id, bits, max_length):
    """Quantize model using AIMET"""
    try:
        from aimet_torch.quantsim import QuantizationSimModel
        import onnx
        import onnxruntime as ort
    except ImportError:
        logger.error("AIMET quantization requires aimet-torch, onnx, and onnxruntime-gpu packages")
        raise
    
    logger.info(f"Quantizing {model_id} to INT{bits} using AIMET...")
    
    # First load the base model
    base_model, tokenizer = load_base_model(model_id, max_length)
    
    # Create dummy input for ONNX export
    dummy_input = tokenizer("This is a test", return_tensors="pt").to(base_model.device)
    
    # Export model to ONNX for AIMET simulation
    onnx_model_path = "temp_model.onnx"
    torch.onnx.export(
        base_model, 
        (dummy_input.input_ids,), 
        onnx_model_path,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "logits": {0: "batch", 1: "sequence"}
        },
        opset_version=14
    )
    
    # Create AIMET quantization simulation
    sim = QuantizationSimModel(
        base_model,
        quant_scheme="tf_enhanced" if bits == 8 else "tf",
        default_output_bw=bits,
        default_param_bw=bits
    )
    
    # Calibrate the model with sample data
    sim.compute_encodings(dummy_input.input_ids, dummy_input.input_ids)
    
    # Get the quantized model
    quantized_model = sim.model
    
    return quantized_model, tokenizer

def apply_qlora(model, tokenizer, dataset_path, output_dir, max_length):
    """Apply QLoRA fine-tuning to the quantized model"""
    logger.info("Applying QLoRA fine-tuning...")
    
    # Load dataset
    if dataset_path.startswith("hf://"):
        # Load from Hugging Face datasets
        dataset_name = dataset_path.replace("hf://", "")
        dataset = load_dataset(dataset_name)
    else:
        # Load from local files
        dataset = load_dataset("json", data_files=dataset_path)
    
    logger.info(f"Loaded dataset with {len(dataset['train'])} examples")
    
    # Configure LoRA
    peft_config = LoraConfig(
        r=16,                     # Rank
        lora_alpha=32,            # Alpha parameter for LoRA scaling
        lora_dropout=0.05,        # Dropout probability for LoRA layers
        bias="none",              # Bias type for LoRA
        task_type="CAUSAL_LM",    # Task type
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    
    # Apply LoRA to model
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    
    # Prepare training arguments
    training_args = TrainingArguments(
        output_dir=os.path.join(output_dir, "qlora_checkpoints"),
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        num_train_epochs=1,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        report_to="none"
    )
    
    # Prepare training data
    def preprocess_function(examples):
        return tokenizer(
            examples["text"], 
            truncation=True,
            max_length=max_length,
            padding="max_length"
        )
    
    processed_dataset = dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=processed_dataset["train"],
        tokenizer=tokenizer
    )
    
    # Train the model
    logger.info("Starting QLoRA fine-tuning...")
    trainer.train()
    
    # Save the fine-tuned model
    logger.info(f"Saving QLoRA fine-tuned model to {output_dir}...")
    model.save_pretrained(output_dir)
    
    return model

def convert_to_gguf(model_dir, output_dir, quant_format="q4_0"):
    """Convert the model to GGUF format for Ollama"""
    logger.info(f"Converting model to GGUF format with {quant_format} quantization...")
    
    # Check if llama.cpp is available, clone if not
    llama_cpp_dir = "./llama.cpp"
    if not os.path.exists(llama_cpp_dir):
        logger.info("Cloning llama.cpp repository...")
        os.system("git clone https://github.com/ggerganov/llama.cpp.git")
        llama_cpp_dir = "./llama.cpp"
    
    # Build llama.cpp if needed
    if not os.path.exists(os.path.join(llama_cpp_dir, "convert.py")):
        logger.info("Building llama.cpp...")
        os.system(f"cd {llama_cpp_dir} && make")
    
    # Convert model to GGUF
    gguf_output = os.path.join(output_dir, f"model_{quant_format}.gguf")
    convert_cmd = (
        f"python3 {llama_cpp_dir}/convert.py "
        f"--input-model {model_dir} "
        f"--output-model {gguf_output} "
        f"--quantize {quant_format}"
    )
    
    logger.info(f"Running conversion command: {convert_cmd}")
    os.system(convert_cmd)
    
    return gguf_output

def benchmark_model(model, tokenizer, prompt="Explain quantum computing in simple terms.", num_runs=5):
    """Benchmark inference speed and quality"""
    logger.info("Benchmarking model performance...")
    
    times = []
    for i in range(num_runs):
        logger.info(f"Benchmark run {i+1}/{num_runs}")
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Warm-up run
        if i == 0:
            with torch.no_grad():
                _ = model.generate(inputs.input_ids, max_new_tokens=20, do_sample=False)
        
        # Timed run
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                do_sample=False
            )
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    tokens_per_second = 100 / avg_time
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    results = {
        "avg_time": avg_time,
        "tokens_per_second": tokens_per_second,
        "output": output_text
    }
    
    logger.info(f"Average generation time: {avg_time:.2f} seconds")
    logger.info(f"Tokens per second: {tokens_per_second:.2f}")
    logger.info(f"Sample output: {output_text}")
    
    return results

def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Step 1: Load and quantize model
    if args.quant_method == "bnb":
        model, tokenizer = quantize_with_bnb(args.model_id, args.bits, args.max_length)
    else:  # AIMET
        model, tokenizer = quantize_with_aimet(args.model_id, args.bits, args.max_length)
    
    # Step 2: Apply QLoRA fine-tuning if requested
    if args.apply_qlora and args.dataset_path:
        model = apply_qlora(model, tokenizer, args.dataset_path, args.output_dir, args.max_length)
    
    # Step 3: Save the quantized model
    logger.info(f"Saving quantized model to {args.output_dir}...")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    
    # Step 4: Benchmark the model
    benchmark_results = benchmark_model(model, tokenizer)
    
    # Step 5: Convert to GGUF if requested
    if args.convert_gguf:
        gguf_path = convert_to_gguf(args.output_dir, args.output_dir, args.gguf_quant)
        logger.info(f"GGUF model saved to {gguf_path}")
        
        # Add instructions for using with Ollama
        logger.info("\nTo use with Ollama, create a modelfile with:")
        logger.info(f"""
FROM {gguf_path}

# System prompt
SYSTEM """
You are a helpful AI assistant.
"""

# Parameters
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "USER:"
""")
        logger.info(f"Then run: ollama create my-quantized-model -f modelfile")

if __name__ == "__main__":
    main()