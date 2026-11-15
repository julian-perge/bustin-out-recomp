#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
GHIDRA_HOME=${GHIDRA_HOME:-/opt/homebrew/Cellar/ghidra/12.2/libexec}
URL=${GHIDRA_MCP_URL:-http://127.0.0.1:8089}
LIST=${1:-$ROOT/build/target/candidates.txt}
# "starts" makes every listed address that is not a function start at the end a reject.
MODE=(${2:+"$2"})
LOG="$ROOT/build/create-functions.log"
REJECTED="$ROOT/build/create-functions-rejected.txt"

if curl -s -m 2 "$URL/check_connection" >/dev/null; then
  echo "Stop the ghidra-mcp server first: it holds the Ghidra project lock." >&2
  exit 1
fi
if [ ! -s "$LIST" ]; then
  echo "Write the address list first: uv run python -m bodecomp.gaps candidates" >&2
  exit 1
fi

mkdir -p "$ROOT/build"
rm -f "$REJECTED"
"$GHIDRA_HOME/support/analyzeHeadless" "$ROOT/ghidra" BustinOut \
  -process default.xbe -noanalysis \
  -scriptPath "$ROOT/tools/ghidra_scripts" \
  -postScript CreateFunctions.java "$LIST" "$REJECTED" ${MODE[@]+"${MODE[@]}"} \
  > "$LOG" 2>&1 || true

if ! grep -q 'functions created' "$LOG"; then
  grep -A 30 'SCRIPT ERROR' "$LOG" >&2 || tail -40 "$LOG" >&2
  exit 1
fi
grep 'removed function\|functions created' "$LOG" | sed 's/^.*> //; s/ (GhidraScript) *$//'
