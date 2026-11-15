#!/usr/bin/env python3
"""
Coolify VPS Fleet Manager — Local GUI Backend Server
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Zero-dependency Python HTTP Server powering the Glassmorphic Desktop GUI HUD.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUI_DIR = os.path.join(BASE_DIR, "gui")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "vps-fleet.json")
CONFIG_EXAMPLE = os.path.join(BASE_DIR, "config", "vps-fleet.example.json")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
MOVER_SCRIPT = os.path.join(SCRIPTS_DIR, "move-resource.py")

PORT = 8450
LOG_BUFFER = []
LOG_LOCK = threading.Lock()


def append_log(msg):
    with LOG_LOCK:
        ts = time.strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        LOG_BUFFER.append(entry)
        if len(LOG_BUFFER) > 500:
            LOG_BUFFER.pop(0)
    print(entry)


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


class FleetGUIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            html_file = os.path.join(GUI_DIR, "index.html")
            if os.path.exists(html_file):
                self._set_headers(200, "text/html; charset=utf-8")
                with open(html_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"index.html not found")

        elif path == "/api/fleet":
            config, config_file = load_config()
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "config": config,
                "config_path": config_file,
                "servers": config.get("servers", [])
            }).encode("utf-8"))

        elif path == "/api/logs":
            with LOG_LOCK:
                logs_copy = list(LOG_BUFFER)
            self._set_headers(200)
            self.wfile.write(json.dumps({"logs": logs_copy}).encode("utf-8"))

        elif path == "/api/snapshots":
            os.makedirs(BACKUPS_DIR, exist_ok=True)
            files = []
            for f in os.listdir(BACKUPS_DIR):
                if f.endswith(".tar.gz") or f.endswith(".zip"):
                    fp = os.path.join(BACKUPS_DIR, f)
                    files.append({
                        "filename": f,
                        "path": fp,
                        "size_mb": round(os.path.getsize(fp) / (1024 * 1024), 2),
                        "modified": time.ctime(os.path.getmtime(fp))
                    })
            self._set_headers(200)
            self.wfile.write(json.dumps({"snapshots": files}).encode("utf-8"))

        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if path == "/api/servers":
            config, _ = load_config()
            servers = config.get("servers", [])
            servers.append({
                "name": body.get("name", f"vps-{len(servers)+1}"),
                "ip": body.get("ip", ""),
                "user": body.get("user", "root"),
                "port": int(body.get("port", 22)),
                "role": body.get("role", "worker"),
                "provider": body.get("provider", "generic"),
                "tags": [body.get("role", "worker"), body.get("provider", "generic")]
            })
            config["servers"] = servers
            save_config(config)
            append_log(f"Added new server: {body.get('name')} ({body.get('ip')})")
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success", "servers": servers}).encode("utf-8"))

        elif path == "/api/servers/delete":
            name = body.get("name")
            config, _ = load_config()
            servers = [s for s in config.get("servers", []) if s.get("name") != name]
            config["servers"] = servers
            save_config(config)
            append_log(f"Removed server: {name}")
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success", "servers": servers}).encode("utf-8"))

        elif path == "/api/test-ssh":
            ip = body.get("ip")
            user = body.get("user", "root")
            port = str(body.get("port", 22))
            append_log(f"Testing SSH connection to {user}@{ip}:{port}...")

            def run_test():
                t0 = time.time()
                cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", "-p", port, f"{user}@{ip}", "uname -s && uptime -p"]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                    latency = round((time.time() - t0) * 1000, 1)
                    if res.returncode == 0:
                        append_log(f"SSH OK: {user}@{ip} ({latency}ms) - {res.stdout.strip()}")
                    else:
                        append_log(f"SSH FAIL: {user}@{ip} - Code {res.returncode}: {res.stderr.strip()[:100]}")
                except Exception as e:
                    append_log(f"SSH ERROR: {user}@{ip} - {str(e)}")

            threading.Thread(target=run_test, daemon=True).start()
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "testing_started"}).encode("utf-8"))

        elif path == "/api/install":
            server_name = body.get("server_name", "all")
            config, config_file = load_config()
            append_log(f"Initiating Coolify installation on: {server_name}")

            def run_deploy():
                if sys.platform == "win32":
                    ps_script = os.path.join(SCRIPTS_DIR, "deploy-all-vps.ps1")
                    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script, "-ConfigFile", config_file]
                else:
                    bash_script = os.path.join(SCRIPTS_DIR, "deploy-all-vps.sh")
                    cmd = ["bash", bash_script, config_file]

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    append_log(line.strip())
                p.wait()
                append_log(f"Installation finished with exit code {p.returncode}")

            threading.Thread(target=run_deploy, daemon=True).start()
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "install_started"}).encode("utf-8"))

        elif path == "/api/move":
            action_type = body.get("type")
            append_log(f"Universal Mover triggered: {action_type}")

            def run_mover():
                if action_type == "volume":
                    cmd = [
                        sys.executable, MOVER_SCRIPT, "move-volume",
                        "--src-ip", body.get("src_ip"),
                        "--src-vol", body.get("src_vol"),
                        "--dst-ip", body.get("dst_ip"),
                        "--dst-vol", body.get("dst_vol")
                    ]
                elif action_type == "coolify":
                    cmd = [
                        sys.executable, MOVER_SCRIPT, "move-coolify",
                        "--src-ip", body.get("src_ip"),
                        "--dst-ip", body.get("dst_ip")
                    ]
                elif action_type == "database":
                    cmd = [
                        sys.executable, MOVER_SCRIPT, "move-db",
                        "--type", body.get("db_type", "postgres"),
                        "--src-ip", body.get("src_ip"),
                        "--container", body.get("container"),
                        "--db", body.get("db"),
                        "--db-user", body.get("db_user"),
                        "--db-pass", body.get("db_pass"),
                        "--dst-ip", body.get("dst_ip"),
                        "--dst-container", body.get("dst_container")
                    ]
                else:
                    append_log(f"Unknown move action: {action_type}")
                    return

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    append_log(line.strip())
                p.wait()
                append_log(f"Move task finished with exit code {p.returncode}")

            threading.Thread(target=run_mover, daemon=True).start()
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "migration_started"}).encode("utf-8"))

        elif path == "/api/snapshot/export":
            ip = body.get("ip")
            append_log(f"Snapshot export requested for: {ip}")

            def run_snap():
                cmd = [sys.executable, MOVER_SCRIPT, "snapshot-export", "--ip", ip]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    append_log(line.strip())
                p.wait()
                append_log("Snapshot export process complete.")

            threading.Thread(target=run_snap, daemon=True).start()
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "snapshot_started"}).encode("utf-8"))

        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")


def run_server():
    server = HTTPServer(("127.0.0.1", PORT), FleetGUIHandler)
    url = f"http://127.0.0.1:{PORT}"
    append_log(f"Coolify Fleet GUI Server listening at {url}")

    def open_browser():
        time.sleep(1)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        append_log("Server stopped.")
        sys.exit(0)


if __name__ == "__main__":
    run_server()
