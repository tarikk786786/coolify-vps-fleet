# Security Guidelines & Hardening Protocol

## 1. Zero Plaintext Secret Rule
- Never commit private SSH keys, password hashes, or API tokens to Git.
- Real keys must reside in:
  - Local workstation: `~/.ssh/id_rsa` or `~/.ssh/id_ed25519`.
  - GitHub Actions: Repository Secrets (`SSH_PRIVATE_KEY`).
  - Workspace Master Credentials: `appinfo11.txt`.

## 2. Remote Host Hardening Protocol
- **SSH Key Only Authentication**: Password authentication should be disabled in `/etc/ssh/sshd_config` (`PasswordAuthentication no`).
- **Firewall Rules**:
  - Ports `22` (SSH), `80` (HTTP), `443` (HTTPS), `8000` (Coolify Dashboard), `6001` (WebSocket) are explicitly allowed via UFW.
  - All other ingress ports are blocked by default.
- **Root Separation**: If running as non-root sudoer (e.g. `ubuntu`), the user must have passwordless sudo for Docker management.

## 3. GitHub App vs Personal Access Token Security
- Coolify GitHub App isolates permissions exclusively to code deployment and commit webhooks.
- Fine-grained repository permissions avoid broad account-wide write access.
- Cryptographic HMAC signatures verify every webhook payload sent from GitHub to Coolify.
