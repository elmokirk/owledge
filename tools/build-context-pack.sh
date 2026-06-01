#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=.
TASK_ID=manual
AGENT_ROLE=worker
OBJECTIVE=

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project-root|-p)
      PROJECT_ROOT=$2
      shift 2
      ;;
    --task-id)
      TASK_ID=$2
      shift 2
      ;;
    --agent-role)
      AGENT_ROLE=$2
      shift 2
      ;;
    --objective)
      OBJECTIVE=$2
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

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

if [ -n "$OBJECTIVE" ]; then
  exec "$PYTHON_BIN" "$SCRIPT_DIR/agent_memory_cli.py" --project-root "$PROJECT_ROOT" build-context-pack --task-id "$TASK_ID" --agent-role "$AGENT_ROLE" --objective "$OBJECTIVE"
fi
exec "$PYTHON_BIN" "$SCRIPT_DIR/agent_memory_cli.py" --project-root "$PROJECT_ROOT" build-context-pack --task-id "$TASK_ID" --agent-role "$AGENT_ROLE"
