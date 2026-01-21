@echo off
echo ========================================
echo Setting up Database Schema
echo ========================================
echo.
echo This will create all tables in your Neon database.
echo.
pause

cd database

echo Creating schema...
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f schema.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Schema creation failed!
    echo Please check your database connection.
    pause
    exit /b 1
)

echo.
echo Creating triggers...
psql "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" -f triggers.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Trigger creation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo All tables have been created.
echo You can now start your backend server.
echo.
pause
