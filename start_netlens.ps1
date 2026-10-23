# NetLens Unified Production Launcher
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    NetLens Unified Production Deployment         " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
try {
    $pyVer = python --version
    Write-Host "[OK] Detected $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Check Nmap
try {
    $nmapVer = (nmap --version)[0]
    Write-Host "[OK] Detected $nmapVer" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Nmap not found in PATH." -ForegroundColor Yellow
}

# 3. Check or build frontend dist
$distPath = Join-Path $scriptDir "netlens\frontend\dist"
if (-not (Test-Path $distPath)) {
    Write-Host "[INFO] Building React production bundle..." -ForegroundColor Yellow
    Push-Location (Join-Path $scriptDir "netlens\frontend")
    npm run build
    Pop-Location
}

Write-Host ""
Write-Host "[INFO] Starting Unified Server at http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "[INFO] API Docs at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Launch browser after 2 seconds
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
} | Out-Null

# Run server
Set-Location (Join-Path $scriptDir "netlens\backend")
python -m uvicorn main:app --host 0.0.0.0 --port 8000
