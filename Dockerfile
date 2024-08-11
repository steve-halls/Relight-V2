# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Install system dependencies and Ollama dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Clone the ComfyUI Repository
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# Replace the Lines in the `server.py` File
RUN sed -i "s/site = web.TCPSite(runner, address, port, ssl_context=ssl_ctx)/site = web.TCPSite(runner, '0.0.0.0', port, ssl_context=ssl_ctx)/" /app/ComfyUI/server.py && \
    sed -i "s/logging.info(\"To see the GUI go to: {}:\/\/{}:{}\".format(scheme, address, port))/logging.info(\"To see the GUI go to: {}:\/\/{}:{}\".format(scheme, '0.0.0.0', port))/" /app/ComfyUI/server.py

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install additional ComfyUI dependencies
RUN pip install --no-cache-dir -r /app/ComfyUI/requirements.txt

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Install Ollama
RUN curl -sSL https://ollama.com/install.sh | bash

# Make the start.sh script executable
RUN chmod +x /app/start.sh

# Set the entry point to the startup script
ENTRYPOINT ["/app/start.sh"]