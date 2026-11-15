# UX Flows & User Journeys — Coolify VPS Fleet Manager & Vercel for VPS

## 1. Custom Domain Connection Journey
```
[User Clicks "Domains" Tab]
           │
           ▼
[Clicks "Add Custom Domain"] ──► Enters "app.tarikislam.in" & picks Project
           │
           ▼
[Control Plane Computes DNS] ──► Displays CNAME / A Record instructions
           │
           ▼
[User configures Cloudflare / DNS Provider]
           │
           ▼
[User Clicks "Verify DNS Now"] ──► Queries Cloudflare 1.1.1.1 DoH
           │
     ┌─────┴────────┐
     ▼              ▼
[Match Found]  [Pending Propagation]
     │              │
Green Badge    Amber Badge (Try again in 60s)
SSL Active
```

## 2. 24/7 Always-Live Cloud VPS Provisioning Journey
```
[User Clicks "24/7 Cloud" Tab]
           │
           ▼
[Selects "Deploy 24/7 to Cloud VPS"]
           │
           ▼
[Enters VPS Public IP + SSH User + Domain]
           │
           ▼
[Automated Runner Executes over SSH]:
  1. apt-get update & install Docker / Docker Compose
  2. UFW firewall allow 22, 80, 443, 8000
  3. curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
  4. Configures APP_URL=https://coolify.tarikislam.in
           │
           ▼
[Server Added to Fleet] ──► 24/7 Always-Live Cloud Control Plane Ready
```
