#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
GHIDRA_HOME=${GHIDRA_HOME:-/opt/homebrew/Cellar/ghidra/12.2/libexec}

if curl -s -m 2 http://127.0.0.1:8089/check_connection >/dev/null; then
  echo "Stop the ghidra-mcp server first: it holds the Ghidra project lock." >&2
  exit 1
fi
# The rebuild discards names that exist only in Ghidra, so run
# "uv run python -m bodecomp.sync export" before stopping the server. Requiring a
# commit means every rebuild starts from a symbols.txt that git can reproduce.
if ! git -C "$ROOT" diff --quiet HEAD -- config/symbols.txt; then
  echo "Commit config/symbols.txt first (after sync export): the rebuild starts from it." >&2
  exit 1
fi

rm -rf "$ROOT/ghidra/BustinOut.gpr" "$ROOT/ghidra/BustinOut.rep"
mkdir -p "$ROOT/ghidra" "$ROOT/build"
"$GHIDRA_HOME/support/analyzeHeadless" "$ROOT/ghidra" BustinOut \
  -import "$ROOT/orig/default.xbe" > "$ROOT/build/ghidra-import.log" 2>&1
grep -q 'Using Loader: Xbox Executable Format' "$ROOT/build/ghidra-import.log" || {
  echo "The XBE loader was not used; see build/ghidra-import.log." >&2
  exit 1
}
# Ghidra's analysis misses functions that only padding leads to (F-0016), and
# symbols.txt lists the ones created since. Creating every listed start that the
# import missed gives the rebuilt project the same functions as the old one.
(cd "$ROOT" && uv run python -m bodecomp.gaps starts)
"$ROOT/tools/create-functions.sh" "$ROOT/build/target/starts.txt" starts
if [ -s "$ROOT/build/create-functions-rejected.txt" ]; then
  echo "Some functions in symbols.txt could not be created; see build/create-functions-rejected.txt." >&2
  exit 1
fi
echo "Rebuilt ghidra/BustinOut. Next: start the server, open default.xbe, then run"
echo "  uv run python -m bodecomp.sync apply && uv run python -m bodecomp.sync check"
