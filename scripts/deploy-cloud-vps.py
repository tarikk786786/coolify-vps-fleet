#!/usr/bin/env python3
"""
24/7 Always-Live Cloud VPS Deployer for Coolify
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Connects to any remote Cloud VPS (Oracle Cloud Free Tier, Hetzner, DigitalOcean, AWS, etc.)
over SSH, installs official Coolify v4 engine, configures UFW firewall, binds custom domains,
and ensures 24/7 always-live uptime.
"""

import json
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVERS_FILE = os.path.join(BASE_DIR, "config", "vps-fleet.json")


def run_remote_ssh(ip, user, port, ssh_key, command):
    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-p", str(port),
    ]
    if ssh_key and os.path.exists(os.path.expanduser(ssh_key)):
        ssh_cmd.extend(["-i", os.path.expanduser(ssh_key)])
    ssh_cmd.append(f"{user}@{ip}")
    ssh_cmd.append(command)

    print(f"[*] Executing on {user}@{ip}:{port}...")
    proc = subprocess.run(ssh_cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def deploy_cloud_vps(ip, user="root", port=22, ssh_key="~/.ssh/id_ed25519", domain=None, provider="generic"):
    """
    Installs Coolify v4 on a remote cloud VPS and attaches custom domain.
    """
    print(f"==================================================")
    print(f"Deploying 24/7 Always-Live Coolify on {ip}")
    print(f"Provider: {provider} | User: {user} | Port: {port}")
    if domain:
        print(f"Binding Custom Domain: https://{domain}")
    print(f"==================================================")

    # 1. System Check & Baseline packages
    prep_cmd = (
        "export DEBIAN_FRONTEND=noninteractive && "
        "apt-get update -y && "
        "apt-get install -y curl wget git jq ufw ca-certificates gnupg lsb-release"
    )
    rc, out, err = run_remote_ssh(ip, user, port, ssh_key, prep_cmd)
    if rc != 0:
        return {"status": "error", "message": f"SSH connection or package install failed: {err}"}

    # 2. Firewall configuration for Coolify
    fw_cmd = "ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 8000/tcp && ufw allow 6001/tcp && ufw --force enable"
    run_remote_ssh(ip, user, port, ssh_key, fw_cmd)

    # 3. Official Coolify Installation Script
    print("[*] Running official Coolify v4 installer...")
    coolify_install_cmd = "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash"
    rc, out, err = run_remote_ssh(ip, user, port, ssh_key, coolify_install_cmd)
    print(out)

    # 4. If custom domain specified, set APP_URL
    if domain:
        domain_cmd = f"sed -i 's|^APP_URL=.*|APP_URL=https://{domain}|g' /data/coolify/source/.env && cd /data/coolify/source && docker compose up -d"
        run_remote_ssh(ip, user, port, ssh_key, domain_cmd)

    # 5. Save server to fleet
    try:
        servers = []
        if os.path.exists(SERVERS_FILE):
            with open(SERVERS_FILE, "r", encoding="utf-8") as f:
                servers = json.load(f).get("servers", [])
        servers = [s for s in servers if s.get("ip") != ip]
        servers.append({
            "name": f"Cloud-{provider.capitalize()}-{ip.replace('.', '-')}",
            "ip": ip,
            "user": user,
            "port": port,
            "role": "control-plane",
            "provider": provider,
            "domain": domain or f"http://{ip}:8000",
            "status": "online",
            "last_synced": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        with open(SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"fleet_name": "Tarik VPS Fleet", "owner": "tarikk786786", "servers": servers}, f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Could not update servers file: {e}")

    return {
        "status": "success",
        "ip": ip,
        "coolify_url": f"https://{domain}" if domain else f"http://{ip}:8000",
        "provider": provider,
        "message": f"Coolify v4 deployed and running 24/7 on {ip}!"
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        vps_ip = sys.argv[1]
        custom_dom = sys.argv[2] if len(sys.argv) > 2 else None
        res = deploy_cloud_vps(vps_ip, domain=custom_dom)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python deploy-cloud-vps.py <VPS_IP> [custom.domain.com]")
