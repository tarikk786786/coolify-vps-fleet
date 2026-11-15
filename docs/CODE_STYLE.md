# Code Style & Engineering Standards

## 1. Shell Script Conventions (Bash)
- Always start with `#!/usr/bin/env bash`.
- Enforce strict error handling: `set -euo pipefail`.
- Use uppercase for environment constants and configuration: `ARCH`, `TOTAL_RAM_MB`.
- Prefix internal helper functions clearly: `log_info`, `log_success`, `check_privileges`.
- Quote all variables to prevent word splitting: `"${CONFIG_FILE}"`.

## 2. PowerShell Script Conventions
- Use standard cmdlet naming: `Verb-Noun` format.
- Set `$ErrorActionPreference = "Stop"` for fail-fast execution.
- Use structured parameter blocks: `[CmdletBinding()] param(...)`.
- Sanitize line endings: convert Windows CRLF to LF when piping scripts across SSH to Linux targets.

## 3. Python Test Conventions
- Adhere strictly to PEP 8 and Python 3.10+ typing standards.
- Use standard `unittest` framework with descriptive assertion failure messages.
