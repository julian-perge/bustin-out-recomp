#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
GHIDRA_HOME=${GHIDRA_HOME:-/opt/homebrew/Cellar/ghidra/12.2/libexec}
TARGET="$ROOT/build/target"

if curl -s -m 2 http://127.0.0.1:8089/check_connection >/dev/null; then
  echo "Stop the ghidra-mcp server first: it holds the Ghidra project lock." >&2
  exit 1
fi
if [ ! -s "$TARGET/units.txt" ]; then
  echo "Write the units list first: uv run python -m bodecomp.split" >&2
  exit 1
fi

rm -rf "$TARGET/text.obj" "$TARGET/relocs.tsv" "$TARGET/symbols.tsv" "$TARGET/units"
"$GHIDRA_HOME/support/analyzeHeadless" "$ROOT/ghidra" BustinOut \
  -process default.xbe -readOnly -noanalysis \
  -scriptPath "$ROOT/tools/ghidra_scripts" \
  -postScript ExportTextObject.java "$TARGET/text.obj" \
  -postScript ExportDelinkTables.java "$TARGET/relocs.tsv" "$TARGET/symbols.tsv" \
  > "$ROOT/build/delink.log" 2>&1 || true

if [ ! -s "$TARGET/text.obj" ] || ! grep -q 'delink tables written' "$ROOT/build/delink.log"; then
  grep -A 30 'SCRIPT ERROR' "$ROOT/build/delink.log" >&2 || tail -40 "$ROOT/build/delink.log" >&2
  exit 1
fi
grep 'delink tables written' "$ROOT/build/delink.log" | sed 's/^.*> //'
cd "$ROOT"
uv run python -m bodecomp.unitsplit
