#!/bin/sh
# backend/ollama_entrypoint.sh

# Start the Ollama server in the background
/bin/ollama serve &

# Capture the process ID
pid=$!

# Wait a few seconds for the server to be ready
sleep 5

# Pull the specific model required
echo "Pulling model: deepseek-r1:8b"
/bin/ollama pull deepseek-r1:8b

echo "Model pull complete. Ollama is ready."

# Wait for the server process to exit
wait $pid 