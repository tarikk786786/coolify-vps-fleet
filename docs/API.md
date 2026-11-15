# API Contracts & Integration Points — Coolify Fleet

## 1. Coolify Internal HTTP API
Coolify exposes a full REST API for programmatic server management:
- **Base Endpoint**: `http://<PRIMARY_VPS_IP>:8000/api/v1`
- **Authentication**: `Authorization: Bearer <COOLIFY_API_TOKEN>`

### Key Endpoints:
- `GET /servers`: Returns list of all connected VPS nodes and health states.
- `POST /servers`: Adds a new remote VPS destination node with SSH key.
- `GET /applications`: Returns all applications linked from GitHub.
- `POST /deploy`: Triggers remote container rebuild and rollout for a specific project.

## 2. GitHub Webhook Payload Format
- **Path**: `/webhooks/source/github/events`
- **Header**: `X-Hub-Signature-256: sha256=<HMAC>`
- **Event**: `push`
- **Payload**:
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "mark-lvi",
    "full_name": "tarikk786786/mark-lvi",
    "html_url": "https://github.com/tarikk786786/mark-lvi"
  },
  "head_commit": {
    "id": "e2ad331...",
    "message": "Update deployment config"
  }
}
```
