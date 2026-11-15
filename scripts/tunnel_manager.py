#!/usr/bin/env python3
"""
Cloudflare Tunnel & Always-Live Manager for Coolify
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Manages persistent Cloudflare tunnels for 24/7 HTTPS access to Coolify & deployed apps.
"""

import json
import os
import re
import subprocess
import sys
import threading
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
TUNNEL_FILE = os.path.join(CONFIG_DIR, "tunnel.json")
LOG_FILE = os.path.join(CONFIG_DIR, "tunnel.log")

CLOUDFLARED_PATHS = [
    r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
    r"C:\Program Files\cloudflared\cloudflared.exe",
    "cloudflared.exe",
    "cloudflared"
]


def find_cloudflared():
    for p in CLOUDFLARED_PATHS:
        if os.path.exists(p):
            return p
    # Try finding in PATH
    try:
        res = subprocess.run(["where", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip().splitlines()[0]
    except Exception:
        pass
    return None


def get_tunnel_status():
    if os.path.exists(TUNNEL_FILE):
        try:
            with open(TUNNEL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"status": "stopped", "url": None, "target": "http://172.30.148.196:8888"}


def start_tunnel(target="http://172.30.148.196:8888"):
    cf_bin = find_cloudflared()
    if not cf_bin:
        return {"status": "error", "message": "cloudflared not found on system."}

    os.makedirs(CONFIG_DIR, exist_ok=True)
    # Stop existing tunnel if running
    stop_tunnel()

    # Launch process
    log_f = open(LOG_FILE, "w", encoding="utf-8")
    cmd = [cf_bin, "tunnel", "--url", target]
    proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT, text=True)

    # Watch log for URL
    url = None
    for _ in range(25):
        time.sleep(0.5)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = re.findall(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", content)
                if matches:
                    url = matches[0]
                    break
        if proc.poll() is not None:
            break

    if url:
        data = {
            "status": "running",
            "url": url,
            "target": target,
            "pid": proc.pid,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provider": "Cloudflare Zero Trust Edge"
        }
        with open(TUNNEL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data
    else:
        return {"status": "failed", "message": "Failed to obtain tunnel URL in 12s. Check tunnel.log."}


def stop_tunnel():
    status = get_tunnel_status()
    pid = status.get("pid")
    if pid:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        except Exception:
            pass
    # Also kill any orphan cloudflared
    try:
        subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], capture_output=True)
    except Exception:
        pass

    if os.path.exists(TUNNEL_FILE):
        data = {"status": "stopped", "url": None, "target": "http://172.30.148.196:8888"}
        with open(TUNNEL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return {"status": "stopped"}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        target = sys.argv[2] if len(sys.argv) > 2 else "http://172.30.148.196:8888"
        print(json.dumps(start_tunnel(target), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "stop":
        print(json.dumps(stop_tunnel(), indent=2))
    else:
        print(json.dumps(get_tunnel_status(), indent=2))
