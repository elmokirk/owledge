#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON_BIN="${AGENT_MEMORY_PYTHON:-python3}"

exec "$PYTHON_BIN" "$SCRIPT_DIR/build_kb_module.py" "$@"
