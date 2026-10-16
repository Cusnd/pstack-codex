#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$script_dir/worktree-audit.py" "$@"
else
  exec python "$script_dir/worktree-audit.py" "$@"
fi
