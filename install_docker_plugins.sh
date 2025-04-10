#!/bin/bash

# Function to install a Docker CLI plugin
install_plugin() {
    PLUGIN_NAME=$1
    echo "Installing Docker CLI plugin: $PLUGIN_NAME"
    docker plugin install $PLUGIN_NAME
}

# List of Docker CLI plugins to install
PLUGINS=(
    "docker/cli:latest"  # Example plugin, replace with actual plugin names
    "docker/compose:latest"  # Docker Compose plugin
    "docker/volume:latest"  # Example volume plugin
    "docker/network:latest"  # Example network plugin
)

# Install each plugin
for PLUGIN in "${PLUGINS[@]}"; do
    install_plugin $PLUGIN
done

echo "All specified Docker CLI plugins have been installed."