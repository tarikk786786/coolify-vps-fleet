<#
.SYNOPSIS
    Coolify Multi-VPS Fleet Installer (PowerShell)
.DESCRIPTION
    Automates the installation and configuration of Coolify across multiple Linux VPS instances
    from a Windows workstation via SSH.
.PARAMETER ConfigFile
    Path to the JSON fleet configuration file (Default: config/vps-fleet.json).
.PARAMETER SshKeyPath
    Path to your SSH private key file.
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "$PSScriptRoot\..\config\vps-fleet.json",
    [string]$SshKeyPath = "$HOME\.ssh\id_rsa"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  COOLIFY MULTI-VPS FLEET DEPLOYMENT RUNNER (WINDOWS POWERSHELL)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

if (-not (Test-Path $ConfigFile)) {
    Write-Warning "Configuration file not found: $ConfigFile"
    Write-Host "Please create $ConfigFile or pass -ConfigFile <path>"
    exit 1
}

$fleet = Get-Content $ConfigFile -Raw | ConvertFrom-Json
$installerPath = Join-Path $PSScriptRoot "install-coolify.sh"

if (-not (Test-Path $installerPath)) {
    Write-Error "Installer script missing at: $installerPath"
    exit 1
}

$installerContent = [System.IO.File]::ReadAllText($installerPath).Replace("`r`n", "`n")

Write-Host "[INFO] Discovered $($fleet.servers.Count) target VPS server(s)." -ForegroundColor Yellow

foreach ($server in $fleet.servers) {
    $name = $server.name
    $ip   = $server.ip
    $user = if ($server.user) { $server.user } else { "root" }
    $port = if ($server.port) { $server.port } else { 22 }
    $role = if ($server.role) { $server.role } else { "worker" }

    Write-Host "`n--------------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "[FLEET] Provisioning node: $name ($user@$ip`:$port) [Role: $role]" -ForegroundColor Green
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

    try {
        $sshArgs = @(
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            "-p", $port
        )
        if (Test-Path $SshKeyPath) {
            $sshArgs += @("-i", $SshKeyPath)
        }

        # Check connectivity
        Write-Host "[INFO] Testing SSH handshake..." -ForegroundColor Gray
        $testResult = & ssh @sshArgs "$user@$ip" "uname -s" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Could not connect to $ip`: $testResult"
            continue
        }

        Write-Host "[INFO] Connected successfully ($testResult). Piping install script to remote bash..." -ForegroundColor Green
        
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = "ssh"
        $processInfo.Arguments = "$($sshArgs -join ' ') $user@$ip bash -s"
        $processInfo.RedirectStandardInput = $true
        $processInfo.UseShellExecute = $false
        $processInfo.CreateNoWindow = $false

        $process = [System.Diagnostics.Process]::Start($processInfo)
        $process.StandardInput.Write($installerContent)
        $process.StandardInput.Close()
        $process.WaitForExit()

        if ($process.ExitCode -eq 0) {
            Write-Host "[SUCCESS] $name ($ip) successfully provisioned with Coolify!" -ForegroundColor Green
        } else {
            Write-Warning "Provisioning completed with exit code: $($process.ExitCode)"
        }
    }
    catch {
        Write-Error "Error provisioning server $name ($ip): $_"
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  FLEET DEPLOYMENT COMPLETED!" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
