# NetLens Unified Production Launcher
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$defaultPort = if ($env:NETLENS_PORT) { [int]$env:NETLENS_PORT } else { 8000 }
$port = $defaultPort
while ((Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0) {
    $port++
}

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
$possibleNmapPaths = @(
    "$env:ProgramFiles(x86)\Nmap\nmap.exe",
    "$env:ProgramFiles\Nmap\nmap.exe",
    "C:\Program Files (x86)\Nmap\nmap.exe",
    "C:\Program Files\Nmap\nmap.exe"
)
$resolvedNmap = $null
foreach ($candidate in $possibleNmapPaths) {
    if ($candidate -and (Test-Path $candidate)) {
        $resolvedNmap = $candidate
        break
    }
}

if ($resolvedNmap) {
    $nmapDir = Split-Path -Parent $resolvedNmap
    $env:Path = "$nmapDir;$env:Path"
    $nmapVer = (nmap --version)[0]
    Write-Host "[OK] Detected $nmapVer" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Nmap not found in the standard install locations. Scanning features may still fail until it is added to PATH." -ForegroundColor Yellow
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
Write-Host "[INFO] Starting Unified Server at http://localhost:$port ..." -ForegroundColor Cyan
Write-Host "[INFO] API Docs at http://localhost:$port/docs" -ForegroundColor Cyan
Write-Host ""

# Launch browser after 2 seconds
Start-Job -ScriptBlock {
    param($url)
    Start-Sleep -Seconds 2
    Start-Process $url
} -ArgumentList "http://localhost:$port" | Out-Null

# Run server
Set-Location (Join-Path $scriptDir "netlens\backend")
$env:PORT = $port
python -m uvicorn main:app --host 0.0.0.0 --port $port
