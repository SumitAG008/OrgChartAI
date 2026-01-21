@echo off
echo Starting HRIS Integration Service...
cd /d %~dp0
cd backend\hris-service
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt
echo Starting HRIS service on port 8002...
uvicorn main:app --reload --port 8002
pause
