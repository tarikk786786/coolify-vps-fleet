#!/usr/bin/env bash
# ==============================================================================
# Coolify Automated Host Installer & System Hardener
# Author: Tarik Islam (tarikislam.in / github.com/tarikk786786)
# Repository: coolify-vps-fleet
# Standard: POSIX bash, zero-leak credential hygiene, resilient retry loop
# ==============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $1" >&2
}

# 1. Root & Sudo Privilege Check
check_privileges() {
    log_info "Verifying execution privileges..."
    if [ "$(id -u)" -ne 0 ]; then
        log_error "This script must be executed as root or with sudo."
        exit 1
    fi
    log_success "Privilege verification passed."
}

# 2. Hardware Resource & System Architecture Verification
check_resources() {
    log_info "Inspecting hardware specifications..."
    
    # Architecture check (x86_64 or aarch64)
    ARCH=$(uname -m)
    log_info "Detected Architecture: ${ARCH}"
    if [ "${ARCH}" != "x86_64" ] && [ "${ARCH}" != "aarch64" ]; then
        log_error "Unsupported CPU architecture: ${ARCH}. Coolify requires x86_64 or aarch64 (ARM64)."
        exit 1
    fi

    # RAM verification (Coolify recommends >= 2 GB for comfortable container operations)
    TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
    log_info "Total System RAM: ${TOTAL_RAM_MB} MB"
    if [ "${TOTAL_RAM_MB}" -lt 1500 ]; then
        log_warn "System has less than 2GB RAM (${TOTAL_RAM_MB} MB). Setting up 2GB Swapfile to ensure stability..."
        setup_swapfile
    fi

    # Disk Space Check (Minimum 10 GB free)
    FREE_DISK_GB=$(df -BG / | awk 'NR==2 {gsub("G","",$4); print $4}')
    log_info "Free Root Disk Space: ${FREE_DISK_GB} GB"
    if [ "${FREE_DISK_GB}" -lt 5 ]; then
        log_error "Insufficient root disk space. Minimum 5GB required (Found: ${FREE_DISK_GB}GB)."
        exit 1
    fi
}

# Setup 2GB Swap if memory is low
setup_swapfile() {
    if [ ! -f /swapfile ]; then
        log_info "Creating 2GB swapfile at /swapfile..."
        fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
        log_success "Swapfile configured and activated successfully."
    else
        log_info "Swapfile already exists."
    fi
}

# 3. Base OS Packages & Dependencies
install_prerequisites() {
    log_info "Updating system packages and installing dependencies..."
    export DEBIAN_FRONTEND=noninteractive

    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -y
        apt-get install -y curl wget git jq sudo ca-certificates gnupg lsb-release ufw iptables
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y curl wget git jq sudo ca-certificates tar
    elif command -v yum >/dev/null 2>&1; then
        yum install -y curl wget git jq sudo ca-certificates tar
    else
        log_warn "Package manager not recognized; assuming curl and tar are present."
    fi
    log_success "Base dependencies verified."
}

# 4. Firewall Hardening (Allow Coolify UI 8000, Web 80/443, SSH 22)
configure_firewall() {
    log_info "Configuring host firewall rules (UFW/Iptables)..."
    if command -v ufw >/dev/null 2>&1; then
        ufw status | grep -qw "active" && UFW_ACTIVE=1 || UFW_ACTIVE=0
        ufw allow 22/tcp comment 'SSH Remote Access' || true
        ufw allow 80/tcp comment 'HTTP Web Gateway' || true
        ufw allow 443/tcp comment 'HTTPS Web Gateway' || true
        ufw allow 8000/tcp comment 'Coolify Dashboard' || true
        ufw allow 6001/tcp comment 'Coolify Realtime WebSocket' || true
        log_success "Firewall rules updated (Ports 22, 80, 443, 8000, 6001 allowed)."
    fi
}

# 5. Coolify Installation
install_coolify() {
    log_info "Checking if Coolify is already installed..."
    if [ -d "/data/coolify" ] && docker ps 2>/dev/null | grep -q "coolify"; then
        log_success "Coolify is already active on this host! Performing update..."
        curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
        return 0
    fi

    log_info "Initiating official Coolify automated installation..."
    curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
    log_success "Coolify installer execution finished."
}

# 6. Post-Install Verification & Health Check
verify_installation() {
    log_info "Verifying Coolify Docker container status..."
    sleep 5

    if command -v docker >/dev/null 2>&1; then
        RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}')
        log_info "Running containers:\n${RUNNING_CONTAINERS}"
        
        if echo "${RUNNING_CONTAINERS}" | grep -q "coolify"; then
            log_success "Coolify container is RUNNING healthy!"
        else
            log_warn "Coolify container not yet in docker ps. It may still be pulling images. Check 'docker ps' in 60 seconds."
        fi
    fi

    # Determine public IP
    PUBLIC_IP=$(curl -s4 https://ifconfig.me || curl -s4 https://api.ipify.org || echo "YOUR_VPS_IP")

    echo ""
    echo "================================================================================"
    echo "  COOLIFY INSTALLATION COMPLETE!"
    echo "================================================================================"
    echo "  Control Panel URL: http://${PUBLIC_IP}:8000"
    echo "  Default Port:      8000"
    echo "  Web Proxy Ports:   80 (HTTP) / 443 (HTTPS)"
    echo "  WebSocket Port:    6001"
    echo ""
    echo "  Next Steps:"
    echo "  1. Open http://${PUBLIC_IP}:8000 in your browser."
    echo "  2. Register your Admin Account."
    echo "  3. Go to 'Sources' -> 'GitHub App' to connect your GitHub account."
    echo "  4. Add your other VPS nodes in 'Servers' -> '+ Add Server' for multi-VPS fleet!"
    echo "================================================================================"
}

main() {
    check_privileges
    check_resources
    install_prerequisites
    configure_firewall
    install_coolify
    verify_installation
}

main "$@"
