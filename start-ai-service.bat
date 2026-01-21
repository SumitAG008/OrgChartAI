@echo off
echo ========================================
echo Starting AI Service
echo ========================================
cd /d %~dp0
cd backend\ai-service

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
echo Installing core dependencies...
pip install -q -r ..\requirements-core.txt
echo Installing AI dependencies...
pip install -q -r ..\requirements-ai.txt

echo.
echo Starting AI service on http://localhost:8001
echo API docs: http://localhost:8001/docs
echo.
uvicorn main:app --reload --port 8001

pause
