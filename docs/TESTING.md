# Testing Strategy & Verification Suite

## 1. Test Architecture
The test suite ensures:
1. Syntax correctness of bash, PowerShell, and YAML files.
2. Declarative schema validation for `config/vps-fleet.json`.
3. Safe execution safeguards (`set -euo pipefail`, privilege escalation checks).

## 2. Test Commands
```bash
# Run unit test suite
python -m unittest discover -s tests -p "test_*.py" -v

# Validate JSON configuration
python -c "import json; json.load(open('config/vps-fleet.example.json'))"

# Dry run deployment syntax (PowerShell)
pwsh -Command "& { .\scripts\deploy-all-vps.ps1 -ConfigFile .\config\vps-fleet.example.json }"
```

## 3. Acceptance Verification Gate
- Unit tests must pass 100% with 0 errors.
- Shell scripts must pass `bash -n` syntax check.
- GitHub Actions workflow YAML must pass schema linting.
