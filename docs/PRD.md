# Product Requirements Document (PRD) — Coolify VPS Fleet Manager & Vercel for VPS

## 1. Executive Summary & Problem Statement
Managing multiple Virtual Private Servers (VPS) across different cloud providers (Oracle Cloud, Hetzner, DigitalOcean, Contabo, AWS) requires repetitive manual provisioning, Docker configuration, port opening, and individual deployment setups.
Coolify is the open-source self-hosted PaaS platform. **Coolify VPS Fleet Manager** provides an automated infrastructure-as-code control plane, Vercel-like web interface, custom domain manager, and 24/7 always-live deployment pipeline to install, manage, and configure Coolify across all user VPS instances and local hosts directly from GitHub (`tarikk786786`).

## 2. Target Personas
- **Full-Stack Developer & Founder**: Wants a seamless Vercel-like push-to-deploy workflow with 1-click custom domain attachment, automated SSL certificates, and zero vendor lock-in.
- **DevOps Engineer & System Admin**: Needs to bootstrap multiple remote nodes into a single, cohesive deployment cluster with minimum manual SSH interaction, automated swap configuration, firewall hardening, and 24/7 always-live cloud guarantees.

## 3. Scope & Key Features
- **Vercel-Like Control Plane GUI (`gui/index.html` & `gui/server.py`)**:
  - Overview: Projects dashboard, framework presets, repository importer, instant visit links.
  - Deployments: Real-time deployment timeline with commit hashes, server targets, and status.
  - Domains Management (Vercel Style): 1-click custom domain connection, automated DNS record generator (A and CNAME records), live DNS propagation verification via Cloudflare 1.1.1.1 DoH, and Let's Encrypt / Cloudflare SSL badges.
  - 24/7 Always-Live Cloud Architecture: 1-click cloud deployer to Oracle Cloud Always-Free ARM, Hetzner, DigitalOcean, or any SSH VPS, plus local Windows silent background auto-start service (`coolify-silent-boot.vbs`).
  - Servers & Fleet: Multi-node server inventory with role separation (control-plane vs worker).
- **Automated Host Hardener & Installer (`install-coolify.sh`)**: Detects system architecture, ensures minimum 2GB RAM (auto-creates 2GB swap if constrained), opens required ports (22, 80, 443, 8000, 6001), installs Docker and Coolify v4.
- **Persistent Cloudflare Zero-Trust Tunnel (`scripts/tunnel_manager.py`)**: Automatic background tunnel supervisor ensuring 24/7 HTTPS access with valid Cloudflare edge SSL, zero open ports required.
- **Custom Domain & DNS Diagnostic Engine (`scripts/domain_manager.py`)**: Real-time DNS resolver testing against public Anycast DNS.
- **GitHub Actions CI/CD (`deploy-coolify.yml`)**: Allows 1-click execution from GitHub Actions dashboard using repository secrets.

## 4. Non-Goals
- Modifying proprietary cloud provider hypervisors.
- Storing unencrypted SSH private keys or plain text root passwords in source control.
- Running mock or simulated services—all endpoints and containers bind to real ports and active networks.

## 5. Definition of Done (DoD)
- All 10 Vibe Coding Blueprint files exist and are verified.
- Custom domain management and 24/7 always-live cloud architectures are fully functional.
- Automated tests pass with 0 errors.
- Repository is initialized and synchronized with GitHub (`https://github.com/tarikk786786/coolify-vps-fleet`).
