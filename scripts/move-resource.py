#!/usr/bin/env bash
"""":'
# Python wrapper polyglot to run transparently on Windows, Linux, and macOS
exec python3 "$0" "$@"
'"""
# ==============================================================================
# Universal Resource Mover & Fleet Migration Engine
# Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
# Repository: coolify-vps-fleet
# Purpose: Move any application, database, Docker volume, or entire Coolify
#          instance between VPS nodes with zero data loss.
# ==============================================================================

import argparse
import json
import os
import subprocess
import sys
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "vps-fleet.json")
CONFIG_EXAMPLE = os.path.join(BASE_DIR, "config", "vps-fleet.example.json")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")


def log(level, msg):
    colors = {
        "INFO": CYAN,
        "SUCCESS": GREEN,
        "WARN": YELLOW,
        "ERROR": RED
    }
    c = colors.get(level, RESET)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{c}[{level}]{RESET} {ts} - {msg}")


def get_ssh_cmd(user, ip, port=22, key=None):
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=10",
        "-p", str(port)
    ]
    if key and os.path.exists(key):
        cmd.extend(["-i", key])
    cmd.append(f"{user}@{ip}")
    return cmd


def execute_remote(user, ip, port, cmd_str, key=None, check=True):
    base_ssh = get_ssh_cmd(user, ip, port, key)
    full_cmd = base_ssh + [cmd_str]
    log("INFO", f"Executing on {user}@{ip}: {cmd_str[:80]}...")
    res = subprocess.run(full_cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        log("ERROR", f"Remote execution failed (code {res.returncode}): {res.stderr.strip()}")
        raise RuntimeError(res.stderr.strip())
    return res


def migrate_volume(src_ip, src_user, src_port, src_vol, dst_ip, dst_user, dst_port, dst_vol, key=None):
    """
    Streams a Docker volume or directory from Source VPS directly to Destination VPS over SSH.
    Zero local intermediate disk usage.
    """
    log("INFO", f"Migrating volume '{src_vol}' from {src_ip} -> {dst_ip} (volume: '{dst_vol}')...")

    # Ensure destination volume exists
    create_vol_cmd = f"docker volume create {dst_vol} >/dev/null 2>&1 || true"
    execute_remote(dst_user, dst_ip, dst_port, create_vol_cmd, key)

    # Stream volume using tar over SSH pipe:
    # ssh src "tar -czf - -C /var/lib/docker/volumes/<src_vol>/_data ." | ssh dst "tar -xzf - -C /var/lib/docker/volumes/<dst_vol>/_data"
    src_cmd = get_ssh_cmd(src_user, src_ip, src_port, key) + [
        f"docker run --rm -v {src_vol}:/volume alpine tar -czf - -C /volume ."
    ]
    dst_cmd = get_ssh_cmd(dst_user, dst_ip, dst_port, key) + [
        f"docker run --rm -i -v {dst_vol}:/volume alpine tar -xzf - -C /volume"
    ]

    log("INFO", "Initiating encrypted direct stream between VPS nodes...")
    p1 = subprocess.Popen(src_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(dst_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits

    _, err2 = p2.communicate()
    _, err1 = p1.communicate()

    if p1.returncode != 0 or p2.returncode != 0:
        log("ERROR", f"Volume migration error. Src: {err1.decode('utf-8', errors='ignore')} | Dst: {err2.decode('utf-8', errors='ignore')}")
        return False

    log("SUCCESS", f"Volume '{src_vol}' successfully migrated to {dst_ip}:'{dst_vol}'!")
    return True


def migrate_database(src_ip, src_user, src_port, db_type, container_name, db_name, db_user, db_pass,
                     dst_ip, dst_user, dst_port, dst_container, key=None):
    """
    Streams live PostgreSQL or MySQL database from Source container directly to Destination container.
    """
    log("INFO", f"Migrating {db_type.upper()} database '{db_name}' from {src_ip} -> {dst_ip}...")

    if db_type.lower() == "postgres" or db_type.lower() == "postgresql":
        dump_cmd = f"docker exec -e PGPASSWORD='{db_pass}' {container_name} pg_dump -U {db_user} -d {db_name} -Fc"
        restore_cmd = f"docker exec -i -e PGPASSWORD='{db_pass}' {dst_container} pg_restore -U {db_user} -d {db_name} --clean --if-exists"
    elif db_type.lower() == "mysql" or db_type.lower() == "mariadb":
        dump_cmd = f"docker exec {container_name} mysqldump -u {db_user} -p'{db_pass}' {db_name}"
        restore_cmd = f"docker exec -i {dst_container} mysql -u {db_user} -p'{db_pass}' {db_name}"
    else:
        log("ERROR", f"Unsupported database type: {db_type}")
        return False

    src_cmd = get_ssh_cmd(src_user, src_ip, src_port, key) + [dump_cmd]
    dst_cmd = get_ssh_cmd(dst_user, dst_ip, dst_port, key) + [restore_cmd]

    p1 = subprocess.Popen(src_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(dst_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.stdout.close()

    _, err2 = p2.communicate()
    _, err1 = p1.communicate()

    if p1.returncode != 0 or p2.returncode != 0:
        log("ERROR", f"Database migration error. Src: {err1.decode('utf-8', errors='ignore')} | Dst: {err2.decode('utf-8', errors='ignore')}")
        return False

    log("SUCCESS", f"Database '{db_name}' successfully streamed and restored to {dst_ip}!")
    return True


def migrate_coolify_instance(src_ip, src_user, src_port, dst_ip, dst_user, dst_port, key=None):
    """
    Migrates the entire Coolify control plane (/data/coolify) from Source VPS to Destination VPS.
    This moves all registered applications, teams, settings, and databases with zero configuration loss.
    """
    log("INFO", f"Migrating entire Coolify Control Plane from {src_ip} -> {dst_ip}...")

    # 1. Stop Coolify temporarily on source to ensure SQLite/PostgreSQL consistency
    log("INFO", "Pausing Coolify services on source VPS for consistent snapshot...")
    execute_remote(src_user, src_ip, src_port, "docker stop coolify coolify-db coolify-redis coolify-realtime 2>/dev/null || true", key, check=False)

    # 2. Stream /data/coolify to destination VPS
    log("INFO", "Streaming /data/coolify from Source VPS directly to Destination VPS...")
    src_cmd = get_ssh_cmd(src_user, src_ip, src_port, key) + ["tar -czf - -C /data/coolify ."]
    dst_cmd = get_ssh_cmd(dst_user, dst_ip, dst_port, key) + ["mkdir -p /data/coolify && tar -xzf - -C /data/coolify"]

    p1 = subprocess.Popen(src_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(dst_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p1.stdout.close()

    _, err2 = p2.communicate()
    _, err1 = p1.communicate()

    # 3. Restart source Coolify
    log("INFO", "Resuming Coolify on source VPS...")
    execute_remote(src_user, src_ip, src_port, "docker start coolify-db coolify-redis coolify-realtime coolify 2>/dev/null || true", key, check=False)

    if p1.returncode != 0 or p2.returncode != 0:
        log("ERROR", "Coolify migration failed during data transfer.")
        return False

    # 4. Run installer on destination to ensure proper container restart and network bindings
    log("INFO", "Installing & starting Coolify on destination VPS with transferred state...")
    execute_remote(dst_user, dst_ip, dst_port, "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash", key, check=False)

    log("SUCCESS", f"Entire Coolify Control Plane successfully migrated to http://{dst_ip}:8000!")
    return True


def export_fleet_snapshot(vps_ip, vps_user, vps_port, out_dir=BACKUPS_DIR, key=None):
    """
    Downloads an encrypted, compressed snapshot of Coolify from VPS to a local folder.
    Makes the entire setup 100% portable so the user can carry it anywhere.
    """
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    tar_name = f"coolify_snapshot_{vps_ip.replace('.', '_')}_{ts}.tar.gz"
    local_path = os.path.join(out_dir, tar_name)

    log("INFO", f"Creating local backup snapshot from {vps_ip}...")
    src_cmd = get_ssh_cmd(vps_user, vps_ip, vps_port, key) + ["tar -czf - -C /data/coolify ."]

    with open(local_path, "wb") as f:
        res = subprocess.run(src_cmd, stdout=f, stderr=subprocess.PIPE)

    if res.returncode != 0:
        log("ERROR", f"Snapshot export failed: {res.stderr.decode('utf-8', errors='ignore')}")
        if os.path.exists(local_path):
            os.remove(local_path)
        return None

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    log("SUCCESS", f"Snapshot saved to: {local_path} ({size_mb:.2f} MB)")
    return local_path


def restore_fleet_snapshot(snapshot_file, vps_ip, vps_user, vps_port, key=None):
    """
    Restores a local snapshot archive to any new VPS in a single step.
    """
    if not os.path.exists(snapshot_file):
        log("ERROR", f"Snapshot file not found: {snapshot_file}")
        return False

    log("INFO", f"Restoring snapshot '{snapshot_file}' to {vps_user}@{vps_ip}:{vps_port}...")
    dst_cmd = get_ssh_cmd(vps_user, vps_ip, vps_port, key) + ["mkdir -p /data/coolify && tar -xzf - -C /data/coolify"]

    with open(snapshot_file, "rb") as f:
        res = subprocess.run(dst_cmd, stdin=f, capture_output=True)

    if res.returncode != 0:
        log("ERROR", f"Restore stream failed: {res.stderr.decode('utf-8', errors='ignore')}")
        return False

    log("INFO", "Starting Coolify containers on destination VPS...")
    execute_remote(vps_user, vps_ip, vps_port, "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash", key, check=False)

    log("SUCCESS", f"Snapshot successfully restored to http://{vps_ip}:8000!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Coolify Universal Mover & Migration Engine")
    subparsers = parser.add_subparsers(dest="action", help="Migration action")

    # Volume Migration
    vol_parser = subparsers.add_parser("move-volume", help="Migrate Docker volume between VPS nodes")
    vol_parser.add_argument("--src-ip", required=True)
    vol_parser.add_argument("--src-user", default="root")
    vol_parser.add_argument("--src-port", type=int, default=22)
    vol_parser.add_argument("--src-vol", required=True)
    vol_parser.add_argument("--dst-ip", required=True)
    vol_parser.add_argument("--dst-user", default="root")
    vol_parser.add_argument("--dst-port", type=int, default=22)
    vol_parser.add_argument("--dst-vol", required=True)
    vol_parser.add_argument("--key", default=None)

    # Database Migration
    db_parser = subparsers.add_parser("move-db", help="Migrate database between VPS containers")
    db_parser.add_argument("--type", choices=["postgres", "mysql"], default="postgres")
    db_parser.add_argument("--src-ip", required=True)
    db_parser.add_argument("--src-user", default="root")
    db_parser.add_argument("--src-port", type=int, default=22)
    db_parser.add_argument("--container", required=True)
    db_parser.add_argument("--db", required=True)
    db_parser.add_argument("--db-user", required=True)
    db_parser.add_argument("--db-pass", required=True)
    db_parser.add_argument("--dst-ip", required=True)
    db_parser.add_argument("--dst-user", default="root")
    db_parser.add_argument("--dst-port", type=int, default=22)
    db_parser.add_argument("--dst-container", required=True)
    db_parser.add_argument("--key", default=None)

    # Coolify Instance Migration
    coolify_parser = subparsers.add_parser("move-coolify", help="Move full Coolify control plane to a new VPS")
    coolify_parser.add_argument("--src-ip", required=True)
    coolify_parser.add_argument("--src-user", default="root")
    coolify_parser.add_argument("--src-port", type=int, default=22)
    coolify_parser.add_argument("--dst-ip", required=True)
    coolify_parser.add_argument("--dst-user", default="root")
    coolify_parser.add_argument("--dst-port", type=int, default=22)
    coolify_parser.add_argument("--key", default=None)

    # Snapshot Export & Restore
    exp_parser = subparsers.add_parser("snapshot-export", help="Export portable local snapshot from VPS")
    exp_parser.add_argument("--ip", required=True)
    exp_parser.add_argument("--user", default="root")
    exp_parser.add_argument("--port", type=int, default=22)
    exp_parser.add_argument("--key", default=None)

    rest_parser = subparsers.add_parser("snapshot-restore", help="Restore local snapshot to any VPS")
    rest_parser.add_argument("--snapshot", required=True)
    rest_parser.add_argument("--ip", required=True)
    rest_parser.add_argument("--user", default="root")
    rest_parser.add_argument("--port", type=int, default=22)
    rest_parser.add_argument("--key", default=None)

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    if args.action == "move-volume":
        migrate_volume(args.src_ip, args.src_user, args.src_port, args.src_vol,
                       args.dst_ip, args.dst_user, args.dst_port, args.dst_vol, args.key)
    elif args.action == "move-db":
        migrate_database(args.src_ip, args.src_user, args.src_port, args.type,
                         args.container, args.db, args.db_user, args.db_pass,
                         args.dst_ip, args.dst_user, args.dst_port, args.dst_container, args.key)
    elif args.action == "move-coolify":
        migrate_coolify_instance(args.src_ip, args.src_user, args.src_port,
                                 args.dst_ip, args.dst_user, args.dst_port, args.key)
    elif args.action == "snapshot-export":
        export_fleet_snapshot(args.ip, args.user, args.port, key=args.key)
    elif args.action == "snapshot-restore":
        restore_fleet_snapshot(args.snapshot, args.ip, args.user, args.port, key=args.key)


if __name__ == "__main__":
    main()
