@echo off
REM Windows PostgreSQL Setup Batch Script for KcartBot
REM ==================================================

echo.
echo ================================================
echo   KcartBot PostgreSQL Setup for Windows
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if PostgreSQL is installed
if not exist "C:\Program Files\PostgreSQL\17\bin\psql.exe" (
    echo ERROR: PostgreSQL 17 not found at C:\Program Files\PostgreSQL\17\bin
    echo Please install PostgreSQL 17 or update the path in this script
    pause
    exit /b 1
)

echo PostgreSQL found at: C:\Program Files\PostgreSQL\17\bin
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install psycopg2-binary
pip install -r requirements.txt
echo.

REM Run PostgreSQL setup
echo Setting up PostgreSQL database...
python windows_postgresql_setup.py --setup
if errorlevel 1 (
    echo ERROR: PostgreSQL setup failed
    pause
    exit /b 1
)

REM Migrate data
echo Migrating data from SQLite...
python windows_postgresql_setup.py --migrate
if errorlevel 1 (
    echo ERROR: Data migration failed
    pause
    exit /b 1
)

REM Test connection
echo Testing PostgreSQL connection...
python windows_postgresql_setup.py --test
if errorlevel 1 (
    echo ERROR: PostgreSQL connection test failed
    pause
    exit /b 1
)

REM Update environment file
echo Updating environment configuration...
python windows_postgresql_setup.py --all
echo.

echo ================================================
echo   Setup completed successfully!
echo ================================================
echo.
echo Next steps:
echo 1. Test MLOps components: python mlops_demo.py
echo 2. Launch dashboard: python launch_dashboard.py
echo 3. Open browser: http://localhost:8501
echo.
echo Manual commands available with:
echo python windows_postgresql_setup.py --manual
echo.

pause
