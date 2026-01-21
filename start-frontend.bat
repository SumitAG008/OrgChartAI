@echo off
echo ========================================
echo Starting Frontend
echo ========================================
cd /d %~dp0
cd frontend

if not exist node_modules (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting frontend on http://localhost:3000
echo.
npm run dev

pause
