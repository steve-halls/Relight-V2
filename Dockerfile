# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl git

# Install Ollama dependencies
RUN apt-get install -y python3 python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the ComfyUI directory into the container
COPY ComfyUI_windows_portable /ComfyUI

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install additional ComfyUI dependencies
RUN pip install --no-cache-dir -r /ComfyUI/ComfyUI/requirements.txt

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Install Ollama
RUN curl -sSL https://ollama.com/install.sh | bash

# Expose the ports for both applications
EXPOSE 8000 11434

# Make the start.sh script executable
RUN chmod +x /app/start.sh

# Set the entry point to the startup script
ENTRYPOINT ["/app/start.sh"]