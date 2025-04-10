# scripts/finetune_model.py
import os
import torch
import transformers
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

# Load preprocessed dataset
dataset = load_dataset('json', data_files='/data/processed/training_data.jsonl')

# Load base model (with CPU fallback for AMD GPU compatibility)
model_id = "meta-llama/Llama-3-8B"
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Configure LoRA for parameter-efficient fine-tuning
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Prepare training arguments
training_args = transformers.TrainingArguments(
    output_dir="/models/lora-output",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
    save_steps=100,
    logging_steps=10,
    report_to="none"
)

# Configure data collator
data_collator = transformers.DataCollatorForLanguageModeling(
    tokenizer=tokenizer, 
    mlm=False
)

# Initialize trainer
trainer = transformers.Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    data_collator=data_collator,
)

# Train model
trainer.train()

# Save trained model
model.save_pretrained("/models/lora-output/final")
tokenizer.save_pretrained("/models/lora-output/final")