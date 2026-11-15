# Technical Architecture — Coolify Multi-VPS Fleet

## 1. System Topology
```
                          +-------------------------------+
                          |   GitHub Repository & Actions |
                          |    (tarikk786786 / Secrets)   |
                          +---------------+---------------+
                                          |
                        SSH / GitHub Actions Runner
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
+-----------------------+     +-----------------------+     +-----------------------+
|  Primary Control VPS  |     |   Remote Worker VPS 1 |     |   Remote Worker VPS 2 |
|   (Oracle / Hetzner)  |     |   (Docker Node)       |     |   (Contabo / DO)      |
|  - Coolify Core 8000  |     |  - Docker Engine      |     |  - Docker Engine      |
|  - Traefik Proxy 443  |     |  - Coolify Helper     |     |  - Coolify Helper     |
|  - PostgreSQL & Redis |     |  - App Containers     |     |  - App Containers     |
+-----------------------+     +-----------------------+     +-----------------------+
        ^                                 ^                                 ^
        |                                 |                                 |
        +=================== SSH Daemon Control Mesh =======================+
```

## 2. Component Breakdown
1. **GitHub Control Layer**:
   - Stores server topologies in `config/vps-fleet.json`.
   - Executes deployment tasks via GitHub Actions with encrypted `SSH_PRIVATE_KEY`.
2. **Local Workstation CLI**:
   - `scripts/deploy-all-vps.ps1` (Windows PowerShell 5.1/7+).
   - `scripts/deploy-all-vps.sh` (POSIX Bash / WSL / Linux / macOS).
3. **Host Installer Agent (`install-coolify.sh`)**:
   - Idempotent script executed remotely over SSH pipe.
   - Detects existing installations, updates in-place, or performs clean setup.
4. **Coolify Central Orchestrator**:
   - Manages Traefik reverse proxy, Let's Encrypt automated TLS, and Docker networks.
   - Dispatches builds to connected worker VPS nodes.
