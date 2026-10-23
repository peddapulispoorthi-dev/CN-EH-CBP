@echo off
title NetLens - Network Security Assessment Framework
cd /d "%~dp0"

set "NETLENS_PORT=8000"
:findport
netstat -ano | findstr ":%NETLENS_PORT% " >nul 2>&1
if not errorlevel 1 (
    set /a NETLENS_PORT+=1
    goto findport
)

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
if exist "C:\Program Files (x86)\Nmap\nmap.exe" (
    set "PATH=C:\Program Files (x86)\Nmap;%PATH%"
    nmap --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Nmap detected.
    ) else (
        echo [WARNING] Nmap installation was detected but is not on PATH.
    )
) else if exist "C:\Program Files\Nmap\nmap.exe" (
    set "PATH=C:\Program Files\Nmap;%PATH%"
    nmap --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Nmap detected.
    ) else (
        echo [WARNING] Nmap installation was detected but is not on PATH.
    )
) else (
    echo [WARNING] Nmap was not detected in the standard install locations.
    echo Please install Nmap or add it to system PATH for full scanning capabilities.
)

:: 3. Build frontend if dist does not exist
if not exist "netlens\frontend\dist" (
    echo [INFO] Building production frontend assets...
    cd netlens\frontend
    call npm run build
    cd ..\..
)

echo [INFO] Starting NetLens Unified Production Server on http://localhost:%NETLENS_PORT% ...
echo [INFO] Swagger API Documentation available at http://localhost:%NETLENS_PORT%/docs
echo.

:: 4. Open dashboard in default browser after 2 seconds
start "" powershell -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:%NETLENS_PORT%'"

:: 5. Launch FastAPI server
cd netlens\backend
set "PORT=%NETLENS_PORT%"
python -m uvicorn main:app --host 0.0.0.0 --port %NETLENS_PORT%

pause
