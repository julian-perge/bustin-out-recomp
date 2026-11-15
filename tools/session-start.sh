#!/bin/bash
# .claude/settings.json runs this at every session start, resume and compaction,
# and Claude reads what it prints, so it stays under 40 lines and always exits 0.
set -uo pipefail

TOOLS=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${CLAUDE_PROJECT_DIR:-$TOOLS}
URL=${GHIDRA_MCP_URL:-http://127.0.0.1:8089}

echo "== Active block of docs/STATUS.md"
if [ -f "$ROOT/docs/STATUS.md" ]; then
  sed -n '/<!-- active:start -->/,/<!-- active:end -->/p' "$ROOT/docs/STATUS.md" \
    | sed '1d;$d' | head -n 20
else
  echo "(docs/STATUS.md is missing)"
fi

echo "== Open and active findings (search docs/FINDINGS.md before investigating)"
if [ -f "$ROOT/docs/FINDINGS.md" ]; then
  (cd "$TOOLS" && uv run --quiet python -m bodecomp.findings summary \
    --path "$ROOT/docs/FINDINGS.md" --limit 12) || echo "(could not read docs/FINDINGS.md)"
else
  echo "(docs/FINDINGS.md is missing)"
fi

echo "== Environment"
if curl -s -m 2 -o /dev/null "$URL/check_connection"; then
  echo "ghidra-mcp: up at $URL"
else
  echo "ghidra-mcp: down (start it with tools/ghidra-mcp-headless.sh)"
fi
branch=$(git -C "$ROOT" branch --show-current 2>/dev/null)
changes=$(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "branch: ${branch:-none}, uncommitted: $changes"
exit 0
