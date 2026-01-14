#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------
# Extract raw LangGraph decision traces
# Localhost (Docker Compose)
#
# Captures full runs bounded by:
#   🚀 Running LangGraph with input
#   POST /api/chat HTTP/1.1" 200 OK
#
# Output is raw stdout, bracketed only.

# NOTE:
# This script is localhost-only.
# Prod traces can be extracted via:
#   ssh <host> "docker service logs thudbot-prod_backend --since <window> | sed -n '/🚀 Running LangGraph/,/POST \/api\/chat/p'"
# and copied back with scp.
#
# A prod wrapper script can be added later if this becomes necessary.

# ---------------------------------------------

NAME="${1:-langgraph_traces}"
WINDOW="${1:-60m}"

CONTAINER_NAME="thudbot-backend"

REPO_ROOT="$(git rev-parse --show-toplevel)"
OUT_DIR="$REPO_ROOT/apps/backend/tests/regression/results/traces"

mkdir -p "$OUT_DIR"

TS=$(date +"%Y%m%d_%H%M%S")
OUT_FILE="$OUT_DIR/${NAME}_${TS}.log"

echo "Extracting traces from container: $CONTAINER_NAME"
echo "Name prefix: $NAME"
echo "Time window: $WINDOW"
echo "Output: $OUT_FILE"
echo

{
  docker logs "$CONTAINER_NAME" --since "$WINDOW" 2>/dev/null \
  | sed -n '/🚀 Running LangGraph/,/POST \/api\/chat/p'
} > "$OUT_FILE"

echo "Done."
