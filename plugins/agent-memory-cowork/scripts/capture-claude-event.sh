#!/usr/bin/env sh
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -n "${AGENT_MEMORY_PYTHON:-}" ]; then
  PYTHON_BIN=$AGENT_MEMORY_PYTHON
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Agent Memory hook skipped: Python not found." >&2
  exit 0
fi

exec "$PYTHON_BIN" "$SCRIPT_DIR/capture-claude-event.py"
