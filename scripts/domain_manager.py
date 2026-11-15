#!/usr/bin/env python3
"""
Domain & DNS Manager for Coolify VPS Fleet
Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
Handles custom domain binding, DNS record generation, propagation checking,
and Coolify Traefik reverse-proxy binding.
"""

import json
import os
import socket
import sys
import time
import urllib.request

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
DOMAINS_FILE = os.path.join(CONFIG_DIR, "domains.json")
SERVERS_FILE = os.path.join(CONFIG_DIR, "vps-fleet.json")


def load_domains():
    if os.path.exists(DOMAINS_FILE):
        try:
            with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_domains(domains):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(DOMAINS_FILE, "w", encoding="utf-8") as f:
        json.dump(domains, f, indent=2)


def check_dns_propagation(domain, expected_target):
    """
    Check if domain resolves to the expected IP or CNAME target.
    Uses socket DNS lookup and falls back to Cloudflare 1.1.1.1 DoH (DNS over HTTPS).
    """
    results = {
        "domain": domain,
        "expected_target": expected_target,
        "resolved_ips": [],
        "cname": None,
        "verified": False,
        "message": ""
    }

    # 1. Local / System Resolver
    try:
        resolved_ip = socket.gethostbyname(domain)
        results["resolved_ips"].append(resolved_ip)
        if expected_target and (resolved_ip == expected_target or expected_target in resolved_ip):
            results["verified"] = True
            results["message"] = f"Domain resolves to {resolved_ip} (Match!)"
            return results
    except Exception as e:
        results["message"] = f"Local lookup: {str(e)}"

    # 2. Public DNS via Cloudflare DNS-over-HTTPS (1.1.1.1)
    try:
        req = urllib.request.Request(
            f"https://cloudflare-dns.com/dns-query?name={domain}&type=A",
            headers={"Accept": "application/dns-json"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "Answer" in data:
                ips = [ans["data"] for ans in data["Answer"] if ans.get("type") == 1]
                results["resolved_ips"].extend([ip for ip in ips if ip not in results["resolved_ips"]])
                cnames = [ans["data"] for ans in data["Answer"] if ans.get("type") == 5]
                if cnames:
                    results["cname"] = cnames[0]
                
                # Check match
                if any(expected_target in str(val) for val in results["resolved_ips"]):
                    results["verified"] = True
                    results["message"] = f"Cloudflare 1.1.1.1 confirms DNS points to {results['resolved_ips'][0]}"
                elif results["cname"] and expected_target in results["cname"]:
                    results["verified"] = True
                    results["message"] = f"Cloudflare 1.1.1.1 confirms CNAME points to {results['cname']}"
                else:
                    results["message"] = f"Resolving to {results['resolved_ips']}, expected {expected_target}"
            else:
                results["message"] = "No A or CNAME record found yet on public DNS"
    except Exception as e:
        if not results["message"]:
            results["message"] = f"DoH query failed: {str(e)}"

    return results


def generate_dns_records(domain, target_ip, cname_target=None):
    """
    Generate exact DNS records that the user needs to paste into Cloudflare / Namecheap / GoDaddy.
    """
    parts = domain.split(".")
    if len(parts) > 2:
        # Subdomain, e.g. coolify.tarikislam.in -> name is 'coolify'
        record_name = parts[0]
        apex_domain = ".".join(parts[1:])
    else:
        # Apex domain, e.g. tarikislam.in -> name is '@'
        record_name = "@"
        apex_domain = domain

    records = [
        {
            "type": "A",
            "name": record_name,
            "domain": domain,
            "apex": apex_domain,
            "content": target_ip,
            "ttl": "Auto (60s - 300s)",
            "proxied": True,
            "purpose": "Points your domain directly to your VPS / Server IP for instant routing"
        }
    ]

    if cname_target:
        records.append({
            "type": "CNAME",
            "name": record_name,
            "domain": domain,
            "apex": apex_domain,
            "content": cname_target,
            "ttl": "Auto",
            "proxied": True,
            "purpose": "Routes domain via Cloudflare Tunnel / Public Edge endpoint without exposing your VPS IP"
        })

    return records


def add_custom_domain(domain, project, server_name="Primary VPS", server_ip="172.30.148.196", port=80, dns_type="A", cname_target=None):
    domains = load_domains()
    # Remove existing if any
    domains = [d for d in domains if d.get("domain") != domain]

    target = cname_target if dns_type == "CNAME" and cname_target else server_ip

    new_dom = {
        "id": f"dom_{abs(hash(domain)) % 1000000}",
        "domain": domain.strip().lower(),
        "project": project,
        "project_id": f"prj_{project.replace('-', '_')}",
        "server_name": server_name,
        "server_ip": server_ip,
        "port": port,
        "dns_type": dns_type,
        "dns_target": target,
        "status": "pending_dns",
        "ssl_status": "ready_to_provision",
        "verified": False,
        "last_checked": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dns_records": generate_dns_records(domain, server_ip, cname_target)
    }

    # Verify right away
    verification = check_dns_propagation(domain, target)
    new_dom["verified"] = verification["verified"]
    if verification["verified"]:
        new_dom["status"] = "configured"
        new_dom["ssl_status"] = "active"

    domains.insert(0, new_dom)
    save_domains(domains)
    return new_dom


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        domain = sys.argv[2]
        target = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
        res = check_dns_propagation(domain, target)
        print(json.dumps(res, indent=2))
    else:
        print("Domain Manager CLI ready.")
