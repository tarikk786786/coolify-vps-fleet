# AI Agent Operating Directives — Coolify Fleet

## 1. Ground Truth & Boundaries
- Primary configuration files: `config/vps-fleet.json`, `appinfo11.txt`.
- Target accounts: GitHub `tarikk786786`.
- Never prompt user for credentials when available in `appinfo11.txt`.

## 2. Execution Safeguards
- Never execute destructive operations (`rm -rf /`, `docker system prune -a --volumes`) without explicit confirmation.
- Ensure all remote scripts check for non-zero exit codes.
- Report real machine output honestly; never fabricate IP addresses or mock statuses when running real commands.
