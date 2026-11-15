# Data Model & Storage — Coolify Multi-VPS Fleet

## 1. Local Configuration Schema (`config/vps-fleet.json`)
The fleet configuration is structured as declarative JSON:

```json
{
  "fleet_name": "String",
  "owner": "String",
  "default_ssh_user": "String",
  "default_ssh_port": 22,
  "servers": [
    {
      "name": "String",
      "ip": "String (IPv4/IPv6)",
      "user": "String",
      "port": 22,
      "role": "control-plane | worker",
      "provider": "oracle | hetzner | contabo | do | aws",
      "region": "String",
      "tags": ["Array of Strings"]
    }
  ]
}
```

## 2. Remote Coolify Internal Database
On the primary control plane VPS, Coolify automatically maintains:
- **Engine**: PostgreSQL 16 (in Docker container `coolify-db`).
- **Cache & Pub/Sub**: Redis 7 (in Docker container `coolify-redis`).
- **Persistent Data Volume**: `/data/coolify/source` and `/data/coolify/ssh`.
- **Database Backup Schedule**: Automatically dumped daily to `/data/coolify/backups`.
