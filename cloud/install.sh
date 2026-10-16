#!/usr/bin/env bash
set -euo pipefail
cd /workspace/pstack-codex
python -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
npm install --prefix /workspace/.onboarding-tools --cache /workspace/.onboarding-cache/npm bun@1.3.14 --no-audit --no-fund
export PATH="/workspace/.onboarding-tools/node_modules/.bin:$PATH"
export BUN_INSTALL_CACHE_DIR=/workspace/.onboarding-cache/bun
cd plugins/pstack-codex/skills/poteto-mode/scripts
bun install --frozen-lockfile
