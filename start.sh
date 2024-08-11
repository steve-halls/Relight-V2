#!/bin/bash

# Start the Ollama server in the background
ollama serve &

# Wait for the server to start
sleep 10

# Pull the Llava model
ollama pull llava

# Start the ComfyUI application
python3 main.py

# Keep the container running
tail -f /dev/null
