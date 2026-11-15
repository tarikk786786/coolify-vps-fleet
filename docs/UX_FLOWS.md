# User Experience Flows — Coolify Multi-VPS Setup

## Flow 1: New VPS Node Provisioning
```
[User acquires new VPS IP] 
           │
           ▼
[Adds entry to config/vps-fleet.json]
           │
           ▼
[Runs ./scripts/deploy-all-vps.ps1]
           │
           ├──► [Handshake OK] ────► [Pipes install-coolify.sh] ──► [Success (Port 8000 Ready)]
           │
           └──► [Handshake Fail] ──► [Logs Timeout/Auth Error] ──► [Prompts user to verify key]
```

## Flow 2: Connecting GitHub Account to Coolify
1. **User opens Coolify UI** at `http://<VPS_IP>:8000`.
2. **Navigates to Sources**: Clicks `GitHub App` -> `+ Add`.
3. **Automated Registration**: Coolify generates GitHub registration URL.
4. **GitHub Approval**: User selects `tarikk786786` and clicks `Install & Authorize`.
5. **Ready**: All repositories now populate in Coolify for 1-click deployments across any connected VPS.
