@echo off
setlocal

echo Starting Autonomous QA Agent via start_app.py...
echo.

REM Always run from the folder where this .bat is located (project root)
cd /d "%~dp0"

REM Check start_app.py exists
if not exist "start_app.py" (
  echo ❌ start_app.py not found. Please run this from the project root.
  exit /b 1
)

REM Pick Python from local venv if available
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=%cd%\.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe"  set "PYTHON=%cd%\venv\Scripts\python.exe"

echo Using Python: %PYTHON%
echo.

REM Run the orchestrator
"%PYTHON%" "start_app.py"

endlocal
