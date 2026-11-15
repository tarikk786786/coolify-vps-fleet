# Technical Architecture — Coolify VPS Fleet Manager & Vercel for VPS

## 1. System Topology & Component Layout

```
                  ┌──────────────────────────────────────────────┐
                  │          Vercel for VPS Control Plane         │
                  │   (Local GUI: :8450 / Background Server)     │
                  └──────────────────────┬───────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│   Primary Node       │      │   Cloud VPS Node     │      │   Cloudflare Edge    │
│   (WSL2 Ubuntu)      │      │   (Oracle/Hetzner)   │      │   Zero-Trust Tunnel  │
│                      │      │                      │      │                      │
│ • Docker Engine      │      │ • Docker Engine      │      │ • Auto HTTPS / SSL   │
│ • Coolify v4.7.5     │      │ • Coolify Worker     │      │ • Custom Domains     │
│ • Traefik Proxy      │      │ • Traefik Proxy      │      │ • Zero Open Ports    │
│ • Port 8888 (Internal)      │ • 24/7 Always-Live   │      │                      │
└──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

## 2. Tech Stack & Invariants
- **Engine**: Official Coolify v4 (`coollabsio/coolify:4.7.5`), Traefik v3.7, PostgreSQL 15, Redis 7.
- **Control Plane**: Python 3 standard library (`http.server`, `urllib.request`, `socket`, `subprocess`). Zero external third-party pip dependencies required.
- **Frontend HUD**: Tailwind CSS v3 (CDN), Geist & Geist Mono typography, Vercel Dark Mode design tokens (`#000000`, `#0A0A0A`, `#1E1E1E`).
- **Edge Routing & SSL**: Cloudflare Zero-Trust Tunnels (`cloudflared` v2026.11.0) and Traefik Let's Encrypt automated ACME HTTP/DNS challenge resolvers.
- **Orchestration**: PowerShell 7+ on Windows, Bash 5+ on Linux, OpenSSH client with Ed25519 cryptography.

## 3. Data Flow & Deployment Lifecycle
1. **Repository Import**: User selects GitHub repository (`tarikk786786/*`) and specifies optional custom domain (e.g. `app.tarikislam.in`).
2. **Domain Allocation**: Control plane registers domain in `config/domains.json`, computes exact DNS records (`A` or `CNAME`), and queries Cloudflare 1.1.1.1 DoH to verify propagation.
3. **Provisioning**: For local nodes, Docker compose spins up containers behind Traefik on port 8888. For Cloud VPS nodes, `deploy-cloud-vps.py` connects over SSH, installs Docker + Coolify, and assigns the custom domain.
4. **Traffic Ingress**: Cloudflare Edge terminates TLS and proxies traffic to the active node, guaranteeing 24/7 uptime.
