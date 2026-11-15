# Coolify VPS Fleet Manager & GitHub Orchestrator

[![CI/CD Fleet Deployment](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml/badge.svg)](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml)
[![Vibe Coding Standard](https://img.shields.io/badge/Standard-Vibe%20Coding%20Blueprint-blue.svg)](docs/)
[![Author](https://img.shields.io/badge/Author-tarikislam.in-green.svg)](https://tarikislam.in)

Automated deployment engine and orchestration system for installing, maintaining, and connecting **Coolify (Self-Hosted Cloud PaaS)** across all your VPS servers (Oracle Cloud, Hetzner, Contabo, DigitalOcean, AWS) directly integrated with your GitHub account (`tarikk786786`).

---

## 🚀 Quick Start

### 1. Instant 1-Liner on Any VPS
To install Coolify directly on any individual Linux VPS, SSH into your server and run:
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```
Once installed, open `http://<YOUR_VPS_IP>:8000` to access the Coolify Control Panel.

---

### 2. Multi-VPS Automated Fleet Deployment (Windows PowerShell)
To deploy Coolify to multiple VPS servers simultaneously from your local machine:

1. Configure your servers in `config/vps-fleet.json` (see `config/vps-fleet.example.json`).
2. Run the PowerShell fleet runner:
```powershell
.\scripts\deploy-all-vps.ps1 -ConfigFile .\config\vps-fleet.json -SshKeyPath "$HOME\.ssh\id_rsa"
```

---

### 3. Deploy via GitHub Actions CI/CD
1. Add your SSH Private Key to your GitHub repository secrets:  
   `Settings` -> `Secrets and variables` -> `Actions` -> `SSH_PRIVATE_KEY`.
2. Commit your server list to `config/vps-fleet.json`.
3. Go to `Actions` -> **Deploy Coolify to VPS Fleet** -> Click **Run workflow**.

---

### 4. Connect GitHub to Coolify ("All Repos for All VPS")
1. Open your Coolify Dashboard at `http://<PRIMARY_VPS_IP>:8000`.
2. Navigate to **Sources** -> **+ Add Source** -> **GitHub App**.
3. Click **Register GitHub App** — Coolify will automatically set up the webhooks and permissions on your GitHub account (`tarikk786786`).
4. Select **All repositories** when prompted.
5. In Coolify, go to **Servers** -> **+ Add Server** to attach each of your other VPS nodes.
6. Now, any repository on your GitHub can be deployed to **any of your VPS servers** with automatic SSL, custom domains, and zero-downtime rolling updates!

See detailed instructions in [docs/UX_FLOWS.md](file:///c:/Users/tarik/Desktop/MY%20TOOLS/apps/coolify-vps-fleet/docs/UX_FLOWS.md) and [scripts/github-app-setup-guide.md](file:///c:/Users/tarik/Desktop/MY%20TOOLS/apps/coolify-vps-fleet/scripts/github-app-setup-guide.md).

---

## 📁 Repository Structure

```
coolify-vps-fleet/
├── .github/
│   └── workflows/
│       └── deploy-coolify.yml       # GitHub Actions automated workflow
├── config/
│   └── vps-fleet.example.json       # Fleet definition template
├── docs/                            # 10 Core Vibe Coding Blueprint files
│   ├── PRD.md
│   ├── DESIGN_SYSTEM.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   ├── CODE_STYLE.md
│   ├── TESTING.md
│   ├── AGENTS.md
│   ├── UX_FLOWS.md
│   └── API.md
├── scripts/
│   ├── install-coolify.sh           # Hardened host installer & resource check
│   ├── deploy-all-vps.sh            # Multi-node bash SSH runner
│   ├── deploy-all-vps.ps1           # Windows PowerShell fleet runner
│   └── github-app-setup-guide.md    # Step-by-step GitHub App binding guide
├── tests/
│   └── test_fleet_config.py         # Automated unit testing suite
└── README.md
```

---

## 🛡️ Requirements & Ports
- **OS**: Ubuntu 22.04/24.04 LTS, Debian 12, or AlmaLinux 9.
- **Hardware**: Minimum 2 GB RAM (auto-swap generated if < 2GB), 10 GB disk space, x86_64 or ARM64.
- **Firewall Ports**:
  - `8000`: Coolify Dashboard
  - `80` & `443`: Traefik Web Proxy & Let's Encrypt SSL
  - `6001`: Real-time WebSockets
  - `22`: SSH Remote Terminal

---

## 🧪 Testing Verification
Run the automated test suite locally:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---
*Maintained by [Tarik Islam](https://tarikislam.in) | Crafted under the Vibe Coding Blueprint Standard.*
