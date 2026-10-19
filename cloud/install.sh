#!/usr/bin/env bash
set -euo pipefail
PSTACK_TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PSTACK_TASK_ROOT"
python -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
npm install --prefix "$PSTACK_TASK_ROOT/work/tools" --cache "$PSTACK_TASK_ROOT/work/cache/npm" bun@1.3.14 --no-audit --no-fund
export PATH="$PSTACK_TASK_ROOT/work/tools/node_modules/.bin:$PATH"
export BUN_INSTALL_CACHE_DIR="$PSTACK_TASK_ROOT/work/cache/bun"
cd plugins/pstack-codex/skills/poteto-mode/scripts
bun install --frozen-lockfile
