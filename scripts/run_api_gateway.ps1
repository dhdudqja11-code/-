$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "====================================================" -ForegroundColor Green
Write-Host "--- [Asking the Heart] AI API Gateway Service Launcher ---" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# 1. Check Port 5000 Active
$Port = 5000
$PortActive = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($PortActive) {
    $ExistingPid = $PortActive.OwningProcess
    Write-Host "[INFO] Flask API Gateway is already running. (PID: $ExistingPid)" -ForegroundColor Yellow
    Write-Host "Skipping duplicate start." -ForegroundColor Yellow
    exit 0
}

# 2. Run Flask in Silent Background
Write-Host "[PROCESS] Starting Flask API Gateway in Silent Background..." -ForegroundColor Cyan
$ScriptPath = Join-Path $PSScriptRoot "..\api_gateway.py"
$ScriptPath = [System.IO.Path]::GetFullPath($ScriptPath)
$WorkDir = [System.IO.Path]::GetDirectoryName($ScriptPath)

Start-Process python -ArgumentList "`"$ScriptPath`"" -WindowStyle Hidden -WorkingDirectory $WorkDir

# Wait for process initialization
Start-Sleep -Seconds 3
$CheckPort = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($CheckPort) {
    $NewPid = $CheckPort.OwningProcess
    Write-Host "[SUCCESS] Flask API Gateway is running on PID: $NewPid!" -ForegroundColor Green
} else {
    Write-Error "[ERROR] Failed to start Flask API Gateway. Please check Python environment."
    exit 1
}
