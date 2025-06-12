#!/bin/bash
set -e

echo "🚀 Starting backend entrypoint script..."

# Run the seed script
echo "🌱 Running seed script..."
python /app/scripts/seed_minimal.py

# Start the FastAPI application
echo "🌐 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload