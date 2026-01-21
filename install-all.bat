@echo off
echo ========================================
echo Installing All Dependencies
echo Including AI Features (USP)
echo ========================================
echo.

cd /d %~dp0

echo Installing for Org Service...
cd backend\org-service
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing core dependencies...
pip install -q -r ..\requirements-core.txt
echo Installing AI dependencies...
pip install -q -r ..\requirements-ai.txt
call deactivate
cd ..\..

echo.
echo Installing for AI Service...
cd backend\ai-service
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing core dependencies...
pip install -q -r ..\requirements-core.txt
echo Installing AI dependencies...
pip install -q -r ..\requirements-ai.txt
call deactivate
cd ..\..

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo AI Features are now available in both services.
echo This is your USP - always enabled!
echo.
pause
