# API Specification — Coolify VPS Fleet Manager Control Plane

## Base URL
`http://127.0.0.1:8450`

## Endpoints

### 1. Health & Infrastructure Status
- **Method**: `GET /api/health`
- **Response**:
```json
{
  "wsl_docker": true,
  "coolify_running": true,
  "coolify_internal_url": "http://172.30.148.196:8888",
  "tunnel_active": true,
  "tunnel_url": "https://showers-theft-garcia-thumbnails.trycloudflare.com",
  "fleet_size": 3,
  "domains_count": 3
}
```

### 2. Custom Domains Management
- **Method**: `GET /api/domains`
  - Returns list of all configured custom domains, their DNS records, target servers, and SSL verification status.
- **Method**: `POST /api/domains/add`
  - Body:
```json
{
  "domain": "app.tarikislam.in",
  "project": "mark-lvi",
  "server_ip": "172.30.148.196",
  "server_name": "Primary VPS",
  "dns_type": "CNAME",
  "cname_target": "showers-theft-garcia-thumbnails.trycloudflare.com"
}
```
- **Method**: `POST /api/domains/verify`
  - Body: `{"domain": "coolify.tarikislam.in", "target": "172.30.148.196"}`
  - Executes live DNS resolution via Cloudflare 1.1.1.1 DoH and system socket resolver to confirm propagation.
- **Method**: `POST /api/domains/delete`
  - Body: `{"domain": "app.tarikislam.in"}`

### 3. Cloudflare 24/7 Tunnel Control
- **Method**: `GET /api/tunnel`
  - Returns current tunnel status, PID, and public HTTPS URL.
- **Method**: `POST /api/tunnel/start`
  - Body: `{"target": "http://172.30.148.196:8888"}`
  - Starts or restarts background Cloudflare Zero-Trust edge tunnel.
- **Method**: `POST /api/tunnel/stop`
  - Gracefully terminates running tunnel process.

### 4. 24/7 Always-Live Cloud VPS Deployment
- **Method**: `POST /api/cloud/deploy`
  - Body:
```json
{
  "ip": "152.67.123.45",
  "user": "root",
  "port": 22,
  "domain": "coolify.tarikislam.in",
  "provider": "oracle"
}
```
  - Spawns background thread to bootstrap remote cloud node over SSH.
