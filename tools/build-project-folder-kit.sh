#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -n "${AGENT_MEMORY_PYTHON:-}" ]; then
  PYTHON_BIN=$AGENT_MEMORY_PYTHON
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Missing Python. Install Python 3 or set AGENT_MEMORY_PYTHON." >&2
  exit 1
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/build_project_folder_kit.py" "$@"
