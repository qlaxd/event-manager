#!/bin/bash
set -e

# Print environment for debugging
echo "Running Rasa entrypoint script..."
echo "Working directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Start Rasa with the required parameters
exec rasa run --model models --enable-api --cors "*" --debug 