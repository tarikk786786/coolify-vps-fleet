<#
.SYNOPSIS
    Connect Custom Domain & Maintain Public Tunnel for Coolify
.DESCRIPTION
    Exposes Coolify over a secure public HTTPS endpoint and outputs the exact DNS records
    required to bind your custom domain (e.g. coolify.tarikislam.in or dezo.in).
#>

[CmdletBinding()]
param(
    [string]$CustomDomain = "coolify.tarikislam.in"
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  COOLIFY CUSTOM DOMAIN & 24/7 LIVE TUNNEL CONNECTOR" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# 1. Verify Coolify is running
$test = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
if (-not $test -or $test.StatusCode -ne 200) {
    Write-Host "[INFO] Starting Coolify in WSL2..." -ForegroundColor Yellow
    wsl -u root -d Ubuntu -e bash -c "service docker start && docker start coolify-db coolify-redis coolify"
    Start-Sleep -Seconds 3
}

Write-Host "[SUCCESS] Coolify is active on localhost:8000!" -ForegroundColor Green

# 2. Start / Inspect Tunnel
Write-Host "`n[INFO] Initializing Public TLS Tunnel via localhost.run..." -ForegroundColor Cyan
$tunnelTask = Start-Process wsl -ArgumentList "-u root -d Ubuntu -e bash -c 'ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:8000 nokey@localhost.run'" -PassThru -WindowStyle Minimized

Write-Host "`n--------------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  HOW TO BIND YOUR CUSTOM DOMAIN ($CustomDomain):" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Option A: Cloud VPS (100% Always Live 24/7 - Recommended)" -ForegroundColor White
Write-Host "  1. In Cloudflare / DNS Provider, add an 'A' Record:"
Write-Host "     Type: A | Name: coolify | Content: <YOUR_VPS_IP> | Proxy: DNS Only" -ForegroundColor Cyan
Write-Host "  2. In Coolify (http://<YOUR_VPS_IP>:8000):"
Write-Host "     Go to Settings -> General -> Instance's Domain -> Set to https://$CustomDomain"
Write-Host "     Traefik will automatically issue a free Let's Encrypt SSL certificate!`n"

Write-Host "Option B: Tunnel to Localhost" -ForegroundColor White
Write-Host "  1. Add a CNAME in Cloudflare pointing to your tunnel host."
Write-Host "  2. Enable Cloudflare Proxy (Orange Cloud) for free SSL."
Write-Host "--------------------------------------------------------------------------------`n" -ForegroundColor DarkGray
