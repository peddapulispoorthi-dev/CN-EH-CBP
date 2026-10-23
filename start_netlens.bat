@echo off
title NetLens - Network Security Assessment Framework
cd /d "%~dp0"

echo ===================================================
echo     NetLens Unified Production Deployment
echo ===================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

:: 2. Check Nmap
nmap --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Nmap was not detected in PATH.
    echo Please install Nmap or add it to system PATH for full scanning capabilities.
)

:: 3. Build frontend if dist does not exist
if not exist "netlens\frontend\dist" (
    echo [INFO] Building production frontend assets...
    cd netlens\frontend
    call npm run build
    cd ..\..
)

echo [INFO] Starting NetLens Unified Production Server on http://localhost:8000 ...
echo [INFO] Swagger API Documentation available at http://localhost:8000/docs
echo.

:: 4. Open dashboard in default browser after 2 seconds
start "" powershell -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8000'"

:: 5. Launch FastAPI server
cd netlens\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
