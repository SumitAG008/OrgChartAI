@echo off
echo ========================================
echo Setting up PostgreSQL Database (Neon)
echo ========================================
echo.
echo This script will help you set up the database tables.
echo.
echo Option 1: Use Neon Console (Recommended)
echo   1. Go to https://console.neon.tech
echo   2. Select your database: neondb
echo   3. Open SQL Editor
echo   4. Copy contents of database/schema.sql
echo   5. Paste and run
echo   6. Copy contents of database/functional_chart_schema.sql
echo   7. Paste and run
echo.
echo Option 2: Use psql command line
echo   Run: psql "YOUR_CONNECTION_STRING" -f database/schema.sql
echo   Run: psql "YOUR_CONNECTION_STRING" -f database/functional_chart_schema.sql
echo.
echo Your connection string:
echo postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require
echo.
echo ========================================
echo Opening database folder...
echo ========================================
start explorer database
echo.
echo Please run the SQL files in Neon Console or via psql.
echo.
pause
