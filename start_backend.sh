#!/bin/bash
# Startup script for FastAPI backend on Render

# Set environment variables
export PYTHONUNBUFFERED=1

# Create necessary directories
mkdir -p /opt/render/project/data/uploads
mkdir -p /opt/render/project/data/outputs
mkdir -p /opt/render/project/data/chroma_db

# Start uvicorn server
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
