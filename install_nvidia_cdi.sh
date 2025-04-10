#!/bin/bash
# Create CDI directory if it doesn't exist
sudo mkdir -p /etc/cdi

# Generate NVIDIA CDI specification
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml 