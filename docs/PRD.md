# Product Requirements Document (PRD) — Coolify VPS Fleet Manager

## 1. Executive Summary & Problem Statement
Managing multiple Virtual Private Servers (VPS) across different cloud providers (Oracle Cloud, Hetzner, DigitalOcean, Contabo, AWS) requires repetitive manual provisioning, Docker configuration, port opening, and individual deployment setups.
Coolify is the open-source self-hosted PaaS platform. This project, **Coolify VPS Fleet Manager**, provides an automated infrastructure-as-code and deployment pipeline to install, manage, and configure Coolify across all user VPS instances directly from GitHub and workstation terminals.

## 2. Target Personas
- **DevOps Engineer & System Admin**: Needs to bootstrap multiple remote nodes into a single, cohesive deployment cluster with minimum manual SSH interaction.
- **Full-Stack Developer**: Wants push-to-deploy capabilities from GitHub (`tarikk786786`) to any VPS with automated SSL and Traefik reverse proxies.

## 3. Scope & Key Features
- **Automated Host Hardener & Installer (`install-coolify.sh`)**: Detects system architecture, ensures minimum 2GB RAM (auto-creates 2GB swap if constrained), opens required ports (22, 80, 443, 8000, 6001), installs Docker and Coolify.
- **Multi-VPS Orchestration Runner (`deploy-all-vps.sh` & `deploy-all-vps.ps1`)**: Iterates through server nodes defined in `vps-fleet.json` and provisions each node over SSH in parallel or sequential pipeline.
- **GitHub Actions CI/CD (`deploy-coolify.yml`)**: Allows 1-click execution from GitHub Actions dashboard using repository secrets.
- **GitHub App Source Integration**: Step-by-step automated binding to GitHub (`tarikk786786`) for automatic webhook listening on pushes.

## 4. Non-Goals
- Modifying proprietary cloud provider hypervisors.
- Storing unencrypted SSH private keys or plain text root passwords in source control.

## 5. Definition of Done (DoD)
- All 10 Vibe Coding Blueprint files exist and are verified.
- Shell and PowerShell scripts execute defensively with strict error handling (`set -euo pipefail`).
- Automated tests pass with 0 errors.
- Repository is initialized and synchronized with GitHub.
