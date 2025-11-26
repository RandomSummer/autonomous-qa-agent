#!/bin/bash
# Startup script for Streamlit frontend on Render

# Set environment variables
export PYTHONUNBUFFERED=1

# Start Streamlit
streamlit run frontend/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true
