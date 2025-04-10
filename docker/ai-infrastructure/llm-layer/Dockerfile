# Use a base image with Python
FROM python:3.9-slim

# Set environment variables
ENV OPENAI_API_KEY=sk-XXXXXX
ENV ANYSCALE_API_KEY=esecret_XXXXXX

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install routellm directly from PyPI instead of copying local code
RUN pip install --no-cache-dir routellm

# Expose the port for the API
EXPOSE 6060

# Command to run the application
CMD ["python", "-m", "routellm.openai_server", "--routers", "mf", "--strong-model", "gpt-4-1106-preview", "--weak-model", "ollama_chat/llama3"]
