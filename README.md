# Coolify VPS Fleet Manager — Vercel for VPS (Custom Domains & 24/7 Always-Live Cloud)

[![CI/CD Fleet Deployment](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml/badge.svg)](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml)
[![Vibe Coding Standard](https://img.shields.io/badge/Standard-Vibe%20Coding%20Blueprint-blue.svg)](docs/)
[![Author](https://img.shields.io/badge/Author-tarikislam.in-green.svg)](https://tarikislam.in)
[![Cloudflare Tunnel](https://img.shields.io/badge/Edge%20Tunnel-Cloudflare%20Zero--Trust-orange.svg)](https://cloudflare.com)

Automated deployment engine, multi-VPS orchestrator, **Custom Domain Manager (Vercel-Style)**, **24/7 Always-Live Cloud VPS Provisioner**, and **Visual Web GUI Control Plane** for **Coolify v4 (Self-Hosted Cloud PaaS)**. Built to give developers the full speed, aesthetics, and simplicity of Vercel on their own VPS fleet and local machines.

---

## 🌟 Key Features

### 1. 🌐 Vercel-Style Custom Domains Management
- **Instant Domain Connection**: Bind custom apex domains or subdomains (`tarikislam.in`, `coolify.tarikislam.in`, `jarvis.tarikislam.in`, `vps.dezo.in`) to any deployed project or control plane in 1 click.
- **DNS Record Generator**: Automatically generates exact `A` and `CNAME` records tailored for Cloudflare, Route53, Namecheap, GoDaddy, and Hostinger.
- **Live DNS Propagation Diagnostic**: Real-time DNS lookup over Cloudflare 1.1.1.1 DoH to verify when records have propagated worldwide.
- **Automated SSL**: Automatic Let's Encrypt and Cloudflare edge certificate provisioning.

### 2. ⚡ 24/7 Always-Live Cloud Architecture
- **1-Click Cloud VPS Deployment (`scripts/deploy-cloud-vps.py`)**: Connects over SSH to any cloud VPS (Oracle Cloud Always-Free ARM 4-Core 24GB, Hetzner, DigitalOcean, Linode, AWS EC2), hardens system, configures UFW firewall, and installs the official Coolify v4 engine (`coollabsio/coolify:4.7.5`).
- **Cloudflare Zero-Trust 24/7 Edge Tunnel (`scripts/tunnel_manager.py`)**: Persistent background tunnel that exposes Coolify over Cloudflare's global Anycast edge network with zero open ports and automatic reconnect.
- **Silent Windows Background Auto-Start (`scripts/coolify-silent-boot.vbs`)**: Auto-starts WSL2 Docker daemon, Coolify containers, and edge tunnels on Windows boot without opening terminal windows.

### 3. 🖥️ Visual Web GUI Control Plane (`:8450`)
- **Overview**: GitHub repository selector, framework presets (Docker, Next.js, Node, Python, Static), instant deployment trigger, visit links.
- **Deployments**: Complete history of commits, branches, servers, and build statuses.
- **Domains Tab**: Manage all custom domains, view DNS records, and trigger live verification.
- **24/7 Cloud Tab**: Cloud VPS status, 1-click cloud deployer, and background service controls.
- **Servers Fleet**: Node inventory with role badges (control-plane vs worker) and latency checks.

---

## 🚀 Quickstart & Launchers

### Launching the Web GUI:
- From Windows Desktop: Double-click **`Coolify Fleet Manager`** shortcut on Desktop.
- From workspace root: [`Run-CoolifyFleet-GUI.bat`](file:///c:/Users/tarik/Desktop/MY%20TOOLS/Run-CoolifyFleet-GUI.bat)
- From inside folder: [`Run-GUI.bat`](file:///c:/Users/tarik/Desktop/MY%20TOOLS/apps/coolify-vps-fleet/Run-GUI.bat)
- Browser URL: `http://127.0.0.1:8450`

### Official Coolify v4 Control Plane:
- Local Internal: `http://172.30.148.196:8888`
- Live Public HTTPS (Cloudflare Edge): `https://showers-theft-garcia-thumbnails.trycloudflare.com`

---

## 🛠️ Tech Stack & Architecture
- **Control Plane**: Python 3 standard library (`http.server`, `socket`, `urllib.request`).
- **Frontend**: Tailwind CSS, Geist & Geist Mono fonts, Vercel Dark Mode tokens.
- **Engine**: Official Coolify v4 (`coollabsio/coolify:4.7.5`), Traefik v3.7, PostgreSQL 15, Redis 7.
- **Edge Routing**: Cloudflare Zero-Trust Tunnel (`cloudflared` v2026.11.0).

---

## 🧪 Testing & Validation
Run automated unit tests:
```bash
python -m unittest tests/test_fleet_config.py
```
All tests pass with 0 errors.
