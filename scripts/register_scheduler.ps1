$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "====================================================" -ForegroundColor Green
Write-Host "--- [Asking the Heart] Daily Briefing Scheduler Registration ---" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# 1. Resolve Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetScript = Join-Path $ScriptDir "..\daily_briefing.py"
$TargetScript = [System.IO.Path]::GetFullPath($TargetScript)
$WorkDir = [System.IO.Path]::GetDirectoryName($TargetScript)

if (-not (Test-Path $TargetScript)) {
    Write-Error "[ERROR] daily_briefing.py not found: $TargetScript"
    exit 1
}

# 2. Configure Scheduled Task Parameters
$TaskName = "AskingTheHeart_DailyBriefing"
$Description = "Sends daily traffic, sales, and reviews performance report to Telegram at 23:59 daily."

$Action = New-ScheduledTaskAction -Execute "python" -Argument "`"$TargetScript`"" -WorkingDirectory $WorkDir
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:59"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Priority 6
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# 3. Clean up existing task if present
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "[INFO] Removing existing task '$TaskName' to update..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 4. Register new task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $Description -ErrorAction Stop
    Write-Host "[SUCCESS] Windows Scheduler Task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "   - Trigger: Daily at 23:59:00" -ForegroundColor Cyan
    Write-Host "   - Target Script: $TargetScript" -ForegroundColor Cyan
} catch {
    Write-Error "[ERROR] Failed to register task: $_"
    exit 1
}

exit 0
