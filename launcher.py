#!/usr/bin/env python3
"""
Coolify VPS Fleet Manager — Interactive Control Center
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Platform: Cross-platform (Windows, Linux, macOS)
"""

import json
import os
import subprocess
import sys
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "vps-fleet.json")
CONFIG_EXAMPLE = os.path.join(BASE_DIR, "config", "vps-fleet.example.json")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{CYAN}================================================================================
   ██████╗ ██████╗  ██████╗ ██╗     ██╗███████╗██╗   ██╗    ███████╗██╗     ███████╗███████╗████████╗
  ██╔════╝██╔═══██╗██╔═══██╗██║     ██║██╔════╝╚██╗ ██╔╝    ██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝
  ██║     ██║   ██║██║   ██║██║     ██║█████╗   ╚████╔╝     █████╗  ██║     █████╗  █████╗     ██║   
  ██║     ██║   ██║██║   ██║██║     ██║██╔══╝    ╚██╔╝      ██╔══╝  ██║     ██╔══╝  ██╔══╝     ██║   
  ╚██████╗╚██████╔╝╚██████╔╝███████╗██║██║        ██║       ██║     ███████╗███████╗███████╗   ██║   
   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝        ╚═╝       ╚═╝     ╚══════╝╚══════╝╚══════╝   ╚═╝   
{RESET}{BOLD}  Multi-VPS Fleet Installer, Health Monitor & GitHub Cloud Orchestrator{RESET}
  Author: Tarik Islam | https://tarikislam.in | GitHub: tarikk786786/coolify-vps-fleet
{CYAN}================================================================================{RESET}
"""
    print(banner)


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f), CONFIG_PATH
    elif os.path.exists(CONFIG_EXAMPLE):
        with open(CONFIG_EXAMPLE, "r", encoding="utf-8") as f:
            return json.load(f), CONFIG_EXAMPLE
    return {"servers": []}, None


def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"{GREEN}[SUCCESS] Configuration saved to {CONFIG_PATH}{RESET}")


def show_fleet_status():
    config, path = load_config()
    print(f"\n{BOLD}[Active Fleet Configuration]{RESET} Source: {path}")
    servers = config.get("servers", [])
    if not servers:
        print(f"{YELLOW}No servers configured yet. Use Option [5] to add a VPS.{RESET}")
        return

    print(f"\n{'#':<3} {'Server Name':<20} {'IP Address':<18} {'Port':<6} {'Role':<14} {'Provider':<12}")
    print("-" * 75)
    for idx, s in enumerate(servers, 1):
        name = s.get("name", "N/A")
        ip = s.get("ip", "N/A")
        port = str(s.get("port", 22))
        role = s.get("role", "worker")
        provider = s.get("provider", "generic")
        print(f"{idx:<3} {name:<20} {ip:<18} {port:<6} {role:<14} {provider:<12}")
    print("-" * 75)


def test_ssh_connectivity():
    config, _ = load_config()
    servers = config.get("servers", [])
    if not servers:
        print(f"{RED}No servers configured to test.{RESET}")
        return

    print(f"\n{CYAN}Testing SSH connectivity and handshake across all VPS nodes...{RESET}")
    for s in servers:
        name = s.get("name", "Unknown")
        ip = s.get("ip")
        port = s.get("port", 22)
        user = s.get("user", "root")

        print(f"\n[Connecting] {name} ({user}@{ip}:{port})...", end="", flush=True)
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-p", str(port),
            f"{user}@{ip}",
            "uname -s && uptime -p"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if res.returncode == 0:
                output = res.stdout.strip().replace("\n", " | ")
                print(f" {GREEN}[ONLINE]{RESET} ({output})")
            else:
                print(f" {RED}[FAILED]{RESET} (Exit Code: {res.returncode})")
        except subprocess.TimeoutExpired:
            print(f" {YELLOW}[TIMEOUT]{RESET} (Host unreachable on port {port})")
        except Exception as e:
            print(f" {RED}[ERROR]{RESET} ({e})")


def run_fleet_installer():
    config, path = load_config()
    servers = config.get("servers", [])
    if not servers:
        print(f"{RED}No servers configured to install.{RESET}")
        return

    print(f"\n{YELLOW}{BOLD}[WARNING] This will install/upgrade Coolify across {len(servers)} VPS node(s).{RESET}")
    confirm = input("Are you sure you want to proceed? (y/N): ").strip().lower()
    if confirm != "y":
        print("Installation canceled.")
        return

    if sys.platform == "win32":
        ps_script = os.path.join(SCRIPTS_DIR, "deploy-all-vps.ps1")
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script, "-ConfigFile", path]
    else:
        bash_script = os.path.join(SCRIPTS_DIR, "deploy-all-vps.sh")
        cmd = ["bash", bash_script, path]

    print(f"\n{CYAN}Launching deployment runner...{RESET}")
    subprocess.run(cmd)


def open_coolify_dashboard():
    config, _ = load_config()
    servers = config.get("servers", [])
    # Find control plane or first server
    primary = next((s for s in servers if s.get("role") == "control-plane"), None)
    if not primary and servers:
        primary = servers[0]

    if not primary:
        print(f"{RED}No servers configured.{RESET}")
        return

    ip = primary.get("ip")
    url = f"http://{ip}:8000"
    print(f"\n{GREEN}Opening Coolify Dashboard in browser: {url}{RESET}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"{YELLOW}Could not auto-open browser: {e}. Open manually at {url}{RESET}")


def add_server_interactive():
    print(f"\n{CYAN}=== Add New VPS Server ==={RESET}")
    name = input("Enter server identifier name (e.g. oracle-vps-1): ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    ip = input("Enter Public IPv4 Address: ").strip()
    if not ip:
        print("IP cannot be empty.")
        return
    user = input("Enter SSH user [default: root]: ").strip() or "root"
    port_in = input("Enter SSH port [default: 22]: ").strip()
    port = int(port_in) if port_in.isdigit() else 22
    role = input("Enter role (control-plane/worker) [default: worker]: ").strip() or "worker"
    provider = input("Enter cloud provider (oracle/hetzner/contabo/aws/do) [default: generic]: ").strip() or "generic"

    config, _ = load_config()
    servers = config.get("servers", [])
    servers.append({
        "name": name,
        "ip": ip,
        "user": user,
        "port": port,
        "role": role,
        "provider": provider,
        "tags": [role, provider]
    })
    config["servers"] = servers
    save_config(config)


def show_github_guide():
    guide_path = os.path.join(SCRIPTS_DIR, "github-app-setup-guide.md")
    if os.path.exists(guide_path):
        with open(guide_path, "r", encoding="utf-8") as f:
            print("\n" + f.read())
    else:
        print(f"{RED}Guide file not found.{RESET}")


def run_unit_tests():
    print(f"\n{CYAN}Executing automated test suite...{RESET}")
    tests_dir = os.path.join(BASE_DIR, "tests")
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", tests_dir, "-p", "test_*.py", "-v"]
    subprocess.run(cmd)


def main_menu():
    while True:
        print_banner()
        show_fleet_status()
        print(f"""
{BOLD}[FLEET COMMAND OPTIONS]{RESET}
  {GREEN}[1]{RESET} Test SSH Connectivity & Latency to All VPS Nodes
  {GREEN}[2]{RESET} Install / Upgrade Coolify on All VPS Nodes
  {GREEN}[3]{RESET} Open Primary Coolify Dashboard in Browser (:8000)
  {GREEN}[4]{RESET} Add New VPS Server Node to Fleet Config
  {GREEN}[5]{RESET} View GitHub App Integration Instructions (tarikk786786)
  {GREEN}[6]{RESET} Run Fleet Test Suite (Unit Tests & Schema Validation)
  {RED}[0]{RESET} Exit
""")
        choice = input(f"{CYAN}Select option [0-6]: {RESET}").strip()
        if choice == "1":
            test_ssh_connectivity()
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            run_fleet_installer()
            input("\nPress Enter to return to menu...")
        elif choice == "3":
            open_coolify_dashboard()
            input("\nPress Enter to return to menu...")
        elif choice == "4":
            add_server_interactive()
            input("\nPress Enter to return to menu...")
        elif choice == "5":
            show_github_guide()
            input("\nPress Enter to return to menu...")
        elif choice == "6":
            run_unit_tests()
            input("\nPress Enter to return to menu...")
        elif choice == "0":
            print(f"\n{GREEN}Exiting Coolify Fleet Manager. Happy deploying!{RESET}")
            break
        else:
            print(f"{RED}Invalid selection. Please choose an option from 0 to 6.{RESET}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nOperation canceled by user.")
        sys.exit(0)
