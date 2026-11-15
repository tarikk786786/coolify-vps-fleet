# Design System & CLI Terminal Interface Standard

## 1. Visual Language & CLI Palette
The fleet manager relies on high-contrast ANSI colors for terminal feedback and log clarity:
- **Primary / Info**: `#38BDF8` (Sky Blue / ANSI `\033[0;34m`)
- **Success / Healthy**: `#22C55E` (Emerald Green / ANSI `\033[0;32m`)
- **Warning / Degraded**: `#EAB308` (Amber Gold / ANSI `\033[1;33m`)
- **Error / Critical**: `#EF4444` (Crimson Red / ANSI `\033[0;31m`)
- **Neutral Dark / Borders**: `#1E293B` (Slate)
- **Background**: `#0F172A` (Midnight)

## 2. Status Output Formatting
Every command log adheres to a standardized structured format:
`[LEVEL] YYYY-MM-DD HH:MM:SS - Message`

Example:
`[INFO] 2026-11-15 20:55:00 - Connecting to node vps-control-plane (192.0.2.10)...`
`[SUCCESS] 2026-11-15 20:55:30 - Coolify container is RUNNING healthy!`

## 3. Web UI Integration Guidelines
For web dashboards or Coolify UI skins:
- Font: Inter / JetBrains Mono for monospace logs.
- Border radius: `8px` (`rounded-lg`).
- Accessible contrast ratio >= 4.5:1 (WCAG AA compliant).
