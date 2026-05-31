$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "====================================================" -ForegroundColor Green
Write-Host "--- [Asking the Heart] AI Solopreneur Master Auto Setup ---" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# 1. Self-Elevation check (Administrator Privilege)
$CurrentUser = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
$IsAdmin = $CurrentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Host "[INFO] Requesting Administrator Privileges. UAC Prompt opening..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "[SUCCESS] Administrator Privileges successfully acquired!" -ForegroundColor Green
Write-Host ""

# 2. Run API Gateway background setup
Write-Host "[1/2] Launching Flask API Gateway Service..." -ForegroundColor Cyan
$ApiScript = Join-Path $PSScriptRoot "run_api_gateway.ps1"
& $ApiScript
Write-Host ""

# 3. Register Telegram scheduler
Write-Host "[2/2] Registering Daily Performance Telegram Briefing Scheduler..." -ForegroundColor Cyan
$SchedulerScript = Join-Path $PSScriptRoot "register_scheduler.ps1"
& $SchedulerScript
Write-Host ""

Write-Host "====================================================" -ForegroundColor Green
Write-Host "--- AI Solopreneur Silent Background Setup Complete! ---" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host "[SYSTEM STATUS]:" -ForegroundColor Green
Write-Host " - Flask API Server is running silently 24/7 on port 5000." -ForegroundColor Cyan
Write-Host " - Telegram Daily Performance report triggers daily at 23:59:00." -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit..."
