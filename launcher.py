#!/usr/bin/env python3
"""
Coolify VPS Fleet Manager — Interactive Control Center & Universal Mover
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Platform: Cross-platform (Windows, Linux, macOS)
Portability: 100% self-contained relative path resolution. Can be moved to any directory or drive.
"""

import json
import os
import subprocess
import sys
import webbrowser

# Dynamic Base Directory Resolution (Zero hardcoding)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "vps-fleet.json")
CONFIG_EXAMPLE = os.path.join(BASE_DIR, "config", "vps-fleet.example.json")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
GUI_DIR = os.path.join(BASE_DIR, "gui")
MOVER_SCRIPT = os.path.join(SCRIPTS_DIR, "move-resource.py")
GUI_SERVER_SCRIPT = os.path.join(GUI_DIR, "server.py")

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
{RESET}{BOLD}  Multi-VPS Fleet Installer, Visual GUI HUD & GitHub Cloud Orchestrator{RESET}
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
    print(f"\n{BOLD}[Active Fleet Configuration]{RESET} Location: {path}")
    servers = config.get("servers", [])
    if not servers:
        print(f"{YELLOW}No servers configured yet. Use Option [4] or GUI to add a VPS.{RESET}")
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


def launch_visual_gui():
    print(f"\n{GREEN}Launching Visual Glassmorphic GUI HUD (http://127.0.0.1:8450)...{RESET}")
    subprocess.run([sys.executable, GUI_SERVER_SCRIPT])


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


def universal_mover_menu():
    print(f"""
{CYAN}================================================================================
  UNIVERSAL RESOURCE MOVER (MIGRATE ANYTHING BETWEEN VPS NODES)
================================================================================{RESET}
  {GREEN}[1]{RESET} Move Docker Persistent Volume (Direct VPS-to-VPS encrypted pipe)
  {GREEN}[2]{RESET} Move Live Database (PostgreSQL or MySQL streaming replication)
  {GREEN}[3]{RESET} Move Entire Coolify Control Plane to New VPS (/data/coolify)
  {GREEN}[4]{RESET} Export Portable Local Snapshot from VPS
  {GREEN}[5]{RESET} Restore Local Snapshot to New VPS
  {RED}[0]{RESET} Back to Main Menu
""")
    subchoice = input(f"{CYAN}Select migration task [0-5]: {RESET}").strip()
    if subchoice == "1":
        src_ip = input("Source VPS IP: ").strip()
        src_vol = input("Source Docker Volume Name: ").strip()
        dst_ip = input("Destination VPS IP: ").strip()
        dst_vol = input("Destination Docker Volume Name: ").strip()
        cmd = [sys.executable, MOVER_SCRIPT, "move-volume",
               "--src-ip", src_ip, "--src-vol", src_vol,
               "--dst-ip", dst_ip, "--dst-vol", dst_vol]
        subprocess.run(cmd)
    elif subchoice == "2":
        db_type = input("Database Type (postgres/mysql) [default: postgres]: ").strip() or "postgres"
        src_ip = input("Source VPS IP: ").strip()
        container = input("Source Container Name: ").strip()
        db_name = input("Database Name: ").strip()
        db_user = input("Database User: ").strip()
        db_pass = input("Database Password: ").strip()
        dst_ip = input("Destination VPS IP: ").strip()
        dst_container = input("Destination Container Name: ").strip()
        cmd = [sys.executable, MOVER_SCRIPT, "move-db",
               "--type", db_type, "--src-ip", src_ip, "--container", container,
               "--db", db_name, "--db-user", db_user, "--db-pass", db_pass,
               "--dst-ip", dst_ip, "--dst-container", dst_container]
        subprocess.run(cmd)
    elif subchoice == "3":
        src_ip = input("Current Coolify Primary VPS IP: ").strip()
        dst_ip = input("New Target VPS IP (Clean server): ").strip()
        print(f"\n{YELLOW}[WARNING] This will transfer all Coolify configs, databases, and apps to {dst_ip}.{RESET}")
        confirm = input("Confirm Coolify Control Plane migration? (y/N): ").strip().lower()
        if confirm == "y":
            cmd = [sys.executable, MOVER_SCRIPT, "move-coolify", "--src-ip", src_ip, "--dst-ip", dst_ip]
            subprocess.run(cmd)
    elif subchoice == "4":
        vps_ip = input("VPS IP to backup: ").strip()
        cmd = [sys.executable, MOVER_SCRIPT, "snapshot-export", "--ip", vps_ip]
        subprocess.run(cmd)
    elif subchoice == "5":
        snapshot = input("Path to local snapshot (.tar.gz): ").strip()
        dst_ip = input("Destination VPS IP: ").strip()
        cmd = [sys.executable, MOVER_SCRIPT, "snapshot-restore", "--snapshot", snapshot, "--ip", dst_ip]
        subprocess.run(cmd)


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
  {CYAN}{BOLD}[G] LAUNCH VISUAL GUI HUD (Browser Dashboard @ :8450){RESET}
  {GREEN}[1]{RESET} Test SSH Connectivity & Latency to All VPS Nodes
  {GREEN}[2]{RESET} Install / Upgrade Coolify on All VPS Nodes
  {GREEN}[3]{RESET} Open Primary Coolify Dashboard in Browser (:8000)
  {GREEN}[4]{RESET} Add New VPS Server Node to Fleet Config
  {GREEN}[5]{RESET} View GitHub App Integration Instructions (tarikk786786)
  {GREEN}[6]{RESET} Run Fleet Test Suite (Unit Tests & Schema Validation)
  {MAGENTA}[7] UNIVERSAL MOVER: Migrate Any App, Database or Volume between VPS{RESET}
  {MAGENTA}[8] Snapshot Fleet: Export Full Backup to Portable Local Archive{RESET}
  {RED}[0]{RESET} Exit
""")
        choice = input(f"{CYAN}Select option [G, 0-8]: {RESET}").strip().upper()
        if choice == "G":
            launch_visual_gui()
            input("\nPress Enter to return to menu...")
        elif choice == "1":
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
        elif choice == "7":
            universal_mover_menu()
            input("\nPress Enter to return to menu...")
        elif choice == "8":
            config, _ = load_config()
            servers = config.get("servers", [])
            primary = next((s for s in servers if s.get("role") == "control-plane"), None) or (servers[0] if servers else None)
            if primary:
                cmd = [sys.executable, MOVER_SCRIPT, "snapshot-export", "--ip", primary.get("ip")]
                subprocess.run(cmd)
            else:
                ip = input("Enter VPS IP to snapshot: ").strip()
                cmd = [sys.executable, MOVER_SCRIPT, "snapshot-export", "--ip", ip]
                subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
        elif choice == "0":
            print(f"\n{GREEN}Exiting Coolify Fleet Manager. Happy deploying!{RESET}")
            break
        else:
            print(f"{RED}Invalid selection. Please choose an option from G, 0 to 8.{RESET}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nOperation canceled by user.")
        sys.exit(0)
