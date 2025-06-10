#!/bin/sh
# backend/ollama_entrypoint.sh

# Add Google DNS servers as fallback
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Start the Ollama server in the background
/bin/ollama serve &

# Capture the process ID
pid=$!

# Wait a few seconds for the server to be ready
sleep 10

# Create a super simple model definition that acts as a fallback
echo "Creating a simple echo model as fallback..."
cat > echo.modelfile << EOL
FROM text-embedding-ada-002

TEMPLATE """
You are a helpful assistant for the UCC Event Manager system. Your primary goal is to provide professional, courteous support to users.

If the user's message contains inappropriate content, profanity, or offensive language:
1. Do not repeat the offensive language
2. Respond politely and redirect the conversation
3. Focus on how you can help with event management instead

Here's the user's message: {{ .Prompt }}

Your professional response:
"""

PARAMETER temperature 0
PARAMETER seed 42
EOL

# Create the echo model (this doesn't require downloading)
/bin/ollama create echo:latest -f echo.modelfile

# Verify the model was created
echo "Created echo model. Verifying..."
/bin/ollama list

echo "Ollama is ready."

# Wait for the server process to exit
wait $pid 