@echo off
echo ========================================
echo Starting Org Service (Backend)
echo ========================================
cd /d %~dp0
cd backend\org-service

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
echo Installing core dependencies...
pip install -q -r ..\requirements-core.txt
echo Installing AI dependencies (USP feature)...
pip install -q -r ..\requirements-ai.txt

echo.
echo Starting server on http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
uvicorn main:app --reload --port 8000

pause
