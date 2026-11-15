<#
.SYNOPSIS
    Installs Coolify & Tunnel as an Automatic 24/7 Background Service on Windows.
.DESCRIPTION
    Creates a Windows Scheduled Task that starts WSL Docker daemon, Coolify containers,
    and Cloudflare tunnel silently on Windows boot/logon without showing any terminal windows.
.AUTHOR
    Tarik Islam (tarikislam.in / github.com/tarikk786786)
#>

$TaskName = "CoolifyFleetManager_247"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BaseDir = Split-Path -Parent $ScriptDir
$VbsPath = Join-Path $ScriptDir "coolify-silent-boot.vbs"

# Generate Silent VBS Launcher
$VbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
' 1. Start Docker Daemon in WSL2 Ubuntu silently
WshShell.Run "wsl -u root -d Ubuntu -e service docker start", 0, True
' 2. Ensure Coolify containers are running
WshShell.Run "wsl -u root -d Ubuntu -e bash -c ""cd /data/coolify/source && docker compose up -d""", 0, True
' 3. Start Cloudflare Tunnel in background
WshShell.Run "python ""$BaseDir\scripts\tunnel_manager.py"" start", 0, False
"@

Set-Content -Path $VbsPath -Value $VbsContent -Encoding UTF8

Write-Host "Registering Windows Scheduled Task: $TaskName..." -ForegroundColor Cyan

$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "24/7 Always-Live Coolify VPS Fleet Manager & Cloudflare Tunnel Supervisor" | Out-Null
    Write-Host "[SUCCESS] Coolify 24/7 Background Service registered! It will now auto-start on Windows boot." -ForegroundColor Green
} catch {
    Write-Host "[!] Note: Administrator privileges may be required to register Scheduled Task." -ForegroundColor Yellow
    Write-Host "Alternatively, $VbsPath has been created and can be run or placed in shell:startup." -ForegroundColor Cyan
}
