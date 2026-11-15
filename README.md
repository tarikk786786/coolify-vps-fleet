# Coolify VPS Fleet Manager & Universal Mover

[![CI/CD Fleet Deployment](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml/badge.svg)](https://github.com/tarikk786786/coolify-vps-fleet/actions/workflows/deploy-coolify.yml)
[![Vibe Coding Standard](https://img.shields.io/badge/Standard-Vibe%20Coding%20Blueprint-blue.svg)](docs/)
[![Author](https://img.shields.io/badge/Author-tarikislam.in-green.svg)](https://tarikislam.in)

Automated deployment engine, multi-VPS orchestrator, and **Universal Resource Mover** for **Coolify (Self-Hosted Cloud PaaS)**. Built to be **100% relocatable and portable** — you can move this folder to any directory, drive, or machine, and move any application, database, or Docker volume between any VPS servers with zero downtime.

---

## ⚡ 100% Portable & Relocatable Architecture
- **Zero Hardcoded Paths**: All scripts, batch files, and tools use dynamic relative path resolution (`%~dp0`, `$PSScriptRoot`, `os.path.dirname`).
- **Move Anywhere**: You can copy or move `coolify-vps-fleet` to any drive (C:, D:, USB, or another machine) and double-click `Run.bat` — it immediately runs without re-configuration.
- **Move Anything Between VPS**: Built-in migration engine to move live databases, Docker volumes, or complete Coolify control planes between servers.

---

## 🚀 Quick Launch

### 1. Interactive Desktop Launchers (Run from Anywhere)
- From workspace root: [`Run-CoolifyFleet.bat`](file:///c:/Users/tarik/Desktop/MY%20TOOLS/Run-CoolifyFleet.bat)
- From inside the project folder: [`Run.bat`](file:///c:/Users/tarik/Desktop/MY%20TOOLS/apps/coolify-vps-fleet/Run.bat)

Both launchers open the interactive terminal control center:
```
[FLEET COMMAND OPTIONS]
  [1] Test SSH Connectivity & Latency to All VPS Nodes
  [2] Install / Upgrade Coolify on All VPS Nodes
  [3] Open Primary Coolify Dashboard in Browser (:8000)
  [4] Add New VPS Server Node to Fleet Config
  [5] View GitHub App Integration Instructions (tarikk786786)
  [6] Run Fleet Test Suite (Unit Tests & Schema Validation)
  [7] UNIVERSAL MOVER: Migrate Any App, Database or Volume between VPS
  [8] Snapshot Fleet: Export Full Backup to Portable Local Archive
  [0] Exit
```

---

## 📦 Universal Mover Engine (`scripts/move-resource.py`)

### 1. Move a Docker Volume Between VPS Nodes
Stream persistent data directly between servers over encrypted SSH:
```bash
python scripts/move-resource.py move-volume \
  --src-ip 1.2.3.4 --src-vol my_data_vol \
  --dst-ip 5.6.7.8 --dst-vol my_data_vol
```

### 2. Move a Live Database
Stream PostgreSQL / MySQL directly into the destination container:
```bash
python scripts/move-resource.py move-db \
  --type postgres \
  --src-ip 1.2.3.4 --container pg-db --db prod_db --db-user postgres --db-pass secret \
  --dst-ip 5.6.7.8 --dst-container pg-db
```

### 3. Move the Entire Coolify Control Plane to a New VPS
Transfers all configuration, databases, registered apps, and SSH keys in one step:
```bash
python scripts/move-resource.py move-coolify \
  --src-ip 1.2.3.4 \
  --dst-ip 5.6.7.8
```

### 4. Export Portable Local Snapshot
```bash
python scripts/move-resource.py snapshot-export --ip 1.2.3.4
```

### 5. Restore Snapshot to Any Fresh VPS
```bash
python scripts/move-resource.py snapshot-restore --snapshot backups/coolify_snapshot.tar.gz --ip 5.6.7.8
```

---

## 🌐 Connect Your GitHub Account (`tarikk786786`)
1. Open Coolify at `http://<PRIMARY_VPS_IP>:8000`.
2. Go to **Sources** > **GitHub App** > **Register GitHub App**.
3. Select account **`tarikk786786`** and choose **All repositories**.
4. In Coolify, go to **Servers** > **+ Add Server** to attach any of your other VPS nodes.
5. You can now deploy any repo to any server with automated Let's Encrypt SSL!

---

## 📁 Repository Layout
```
coolify-vps-fleet/
├── .github/workflows/deploy-coolify.yml # GitHub Actions workflow
├── backups/                             # Local portable snapshots
├── config/vps-fleet.example.json        # Fleet configuration template
├── docs/                                # 10 Vibe Coding Blueprint files
├── scripts/
│   ├── install-coolify.sh               # Hardened host installer
│   ├── deploy-all-vps.sh                # Bash multi-VPS runner
│   ├── deploy-all-vps.ps1               # PowerShell multi-VPS runner
│   ├── move-resource.py                 # Universal resource mover CLI
│   └── github-app-setup-guide.md        # GitHub App setup guide
├── templates/
│   ├── compose/                         # Production Compose stacks
│   └── github-action-auto-deploy.yml    # Reusable deploy action
├── tests/test_fleet_config.py           # Automated unit tests (5/5 passing)
├── launcher.py                          # Interactive CLI Control Center
├── Run.bat                              # 100% Relocatable launcher
└── README.md
```

---
*Maintained by [Tarik Islam](https://tarikislam.in) | Crafted under the Vibe Coding Blueprint Standard.*
