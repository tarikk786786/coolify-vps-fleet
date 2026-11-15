#!/usr/bin/env bash
# ==============================================================================
# Fleet Deployment Runner: Distribute Coolify Installation to Multiple VPS Servers
# ==============================================================================

set -euo pipefail

CONFIG_FILE="${1:-config/vps-fleet.json}"
SSH_KEY="${SSH_PRIVATE_KEY_PATH:-~/.ssh/id_rsa}"

if [ ! -f "${CONFIG_FILE}" ]; then
    echo "[ERROR] Configuration file '${CONFIG_FILE}' not found."
    echo "Usage: ./deploy-all-vps.sh [path/to/fleet-config.json]"
    exit 1
fi

echo "================================================================================"
echo "  COOLIFY MULTI-VPS FLEET DEPLOYMENT"
echo "  Target Configuration: ${CONFIG_FILE}"
echo "================================================================================"

SERVERS_COUNT=$(jq '.servers | length' "${CONFIG_FILE}")
echo "[INFO] Found ${SERVERS_COUNT} VPS target(s) to provision."

for i in $(seq 0 $((SERVERS_COUNT - 1))); do
    SERVER_NAME=$(jq -r ".servers[$i].name" "${CONFIG_FILE}")
    SERVER_IP=$(jq -r ".servers[$i].ip" "${CONFIG_FILE}")
    SERVER_USER=$(jq -r ".servers[$i].user // \"root\"" "${CONFIG_FILE}")
    SERVER_PORT=$(jq -r ".servers[$i].port // 22" "${CONFIG_FILE}")
    ROLE=$(jq -r ".servers[$i].role // \"worker\"" "${CONFIG_FILE}")

    echo ""
    echo "--------------------------------------------------------------------------------"
    echo "[FLEET] Provisioning node: ${SERVER_NAME} (${SERVER_USER}@${SERVER_IP}:${SERVER_PORT}) [Role: ${ROLE}]"
    echo "--------------------------------------------------------------------------------"

    # Copy installer and execute over SSH
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p "${SERVER_PORT}" -i "${SSH_KEY}" "${SERVER_USER}@${SERVER_IP}" "uname -a" >/dev/null 2>&1; then
        echo "[INFO] Connection established. Uploading and executing install-coolify.sh..."
        ssh -o StrictHostKeyChecking=no -p "${SERVER_PORT}" -i "${SSH_KEY}" "${SERVER_USER}@${SERVER_IP}" "bash -s" < "$(dirname "$0")/install-coolify.sh"
        echo "[SUCCESS] Node ${SERVER_NAME} (${SERVER_IP}) deployment complete!"
    else
        echo "[ERROR] Failed to connect to ${SERVER_NAME} (${SERVER_IP}) via SSH."
    fi
done

echo ""
echo "================================================================================"
echo "  FLEET DEPLOYMENT PROCESS FINISHED!"
echo "================================================================================"
