#!/bin/bash
# run.sh - Start both FastAPI and Streamlit servers (Linux/Mac)

echo "🚀 Starting Autonomous QA Agent..."
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected"
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    exit 1
fi

# Check .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please create .env file with GROQ_API_KEY"
    exit 1
fi

# Start FastAPI backend in background
echo "📡 Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --reload --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to start
sleep 3

# Start Streamlit frontend
echo "🎨 Starting Streamlit frontend on port 8501..."
streamlit run frontend/app.py

# Cleanup on exit
trap "kill $FASTAPI_PID" EXIT