#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
. "$ROOT/tools/env.sh"
URL=${GHIDRA_MCP_URL:-http://127.0.0.1:8089}
OUT=${1:-$ROOT/build/strings.tsv}
LOG="$ROOT/build/export-strings.log"

if curl -s -m 2 "$URL/check_connection" >/dev/null; then
  echo "Stop the ghidra-mcp server first: it holds the Ghidra project lock." >&2
  exit 1
fi

mkdir -p "$ROOT/build" "$(dirname "$OUT")"
# Ghidra runs the script from its own directory, so the output path is made absolute.
OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
"$GHIDRA_HOME/support/analyzeHeadless" "$ROOT/ghidra" BustinOut \
  -process default.xbe -noanalysis -readOnly \
  -scriptPath "$ROOT/tools/ghidra_scripts" \
  -postScript ExportStringRefs.java "$OUT" \
  > "$LOG" 2>&1 || true

if ! grep -q 'string references' "$LOG"; then
  grep -A 30 'SCRIPT ERROR' "$LOG" >&2 || tail -40 "$LOG" >&2
  exit 1
fi
grep 'string references' "$LOG" | sed 's/^.*> //; s/ (GhidraScript) *$//'
