#!/bin/bash
set -euo pipefail

# Fills build/decomp-tree with Ghidra's decompiled C of every function, through the
# running ghidra-mcp server. The server keeps one decompiler open for the sweep, so
# it is much faster than one force_decompile call per function. A tree that is
# already there is adopted, and swept again only when it does not match the
# program. The script waits until the sweep ends and exits 0 only when its phase
# is complete.

ROOT=$(cd "$(dirname "$0")/.." && pwd)
API=${GHIDRA_MCP_URL:-http://127.0.0.1:8089}
POLL=${DECOMP_TREE_POLL_SECONDS:-15}
TREE_ROOT="$ROOT/build/decomp-tree"

if ! curl -s -m 2 "$API/check_connection" >/dev/null; then
  echo "Start the ghidra-mcp server first: tools/ghidra-mcp-headless.sh" >&2
  exit 1
fi

post() {
  curl -s -X POST -H 'Content-Type: application/json' --data "$2" "$API$1"
}

fail_on_error() {
  local error
  error=$(jq -r '.error // empty' <<<"$1")
  if [ -n "$error" ]; then
    echo "$2: $error" >&2
    exit 1
  fi
}

created=$(post "/decompile_tree_create?program=default.xbe" \
  "$(jq -cn --arg root "$TREE_ROOT" '{root: $root}')")
fail_on_error "$created" "decompile_tree_create"
tree=$(jq -r '.tree_id' <<<"$created")

# A sweep decompiles every function again, even when the adopted tree already
# matches the program.
if [ "$(jq -r '"\(.phase) \(.in_sync)"' <<<"$created")" = "complete true" ]; then
  echo "The tree in $TREE_ROOT is already up to date."
  exit 0
fi

started=$(post "/decompile_tree_run" \
  "$(jq -cn --arg tree "$tree" '{tree: $tree, action: "start"}')")
fail_on_error "$started" "decompile_tree_run"

while :; do
  status=$(curl -s "$API/decompile_tree_status?tree=$tree")
  fail_on_error "$status" "decompile_tree_status"
  phase=$(jq -r '.phase' <<<"$status")
  progress=$(jq -r '"\(.functions_done) of \(.functions_total) functions, \(.functions_failed) failed"' <<<"$status")
  echo "$phase: $progress"
  case "$phase" in
    complete)
      echo "The tree is in $TREE_ROOT."
      exit 0
      ;;
    failed | cancelled | stale)
      echo "The sweep ended as $phase. See $TREE_ROOT/STATUS.md." >&2
      exit 1
      ;;
  esac
  sleep "$POLL"
done
