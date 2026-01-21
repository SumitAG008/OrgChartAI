@echo off
echo Setting up HRIS field mapping tables...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Run the setup script
python setup-hris-mapping-tables.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create tables
    echo.
    echo Alternative: Run the SQL file directly:
    echo psql -d your_database -f database/hris_mapping_schema.sql
    pause
    exit /b 1
)

echo.
echo Setup complete!
pause
