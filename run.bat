@echo off
echo Starting Autonomous QA Agent...
echo.

REM Check virtual environment
if not defined VIRTUAL_ENV (
    echo Virtual environment not detected
    echo Please activate: venv\Scripts\activate
    exit /b 1
)

REM Check .env file
if not exist .env (
    echo .env file not found
    echo Please create .env with GROQ_API_KEY
    exit /b 1
)

REM Start FastAPI
echo Starting FastAPI backend on port 8000...
start /b uvicorn backend.main:app --reload --port 8000

REM Wait
timeout /t 3 /nobreak >nul

REM Start Streamlit
echo Starting Streamlit frontend on port 8501...
streamlit run frontend/app.py
