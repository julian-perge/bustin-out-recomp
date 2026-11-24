#!/bin/bash
# .claude/settings.json runs this at every session start, resume and compaction,
# and Claude reads what it prints, so it stays under 40 lines and always exits 0.
# Each line comes from one source. When a source is missing or fails, the hook
# prints one line for it and goes on (ADR-0021).
set -uo pipefail

TOOLS=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${CLAUDE_PROJECT_DIR:-$TOOLS}
URL=${GHIDRA_MCP_URL:-http://127.0.0.1:8089}

# macOS has no timeout command, so the limit applies only where the command exists.
LIMIT=()
if command -v timeout >/dev/null 2>&1; then
  LIMIT=(timeout 4)
fi

# GitHub and agent-skills answers are kept for 60 seconds, because the hook with five
# network calls took more than 3 seconds (ADR-0021). A session start, a resume and a
# compaction in a row then cost one set of calls.
CACHE=${BODECOMP_HOOK_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/bodecomp-hook}/$(printf '%s' "$ROOT" | tr '/' '_')

# remote KEY CMD...: prints the output of CMD, run in the repo. Fails when CMD fails.
remote() {
  local key=$1 file out
  shift
  file="$CACHE/$key"
  if [ -n "$(find "$file" -mmin -1 2>/dev/null)" ]; then
    cat "$file"
    return 0
  fi
  out=$(cd "$ROOT" && "${LIMIT[@]+"${LIMIT[@]}"}" "$@" 2>/dev/null) || return 1
  mkdir -p "$CACHE" 2>/dev/null && printf '%s\n' "$out" >"$file" 2>/dev/null
  printf '%s\n' "$out"
}

# gh_list NAME CAP -- ARGS...: runs gh in the repo and prints at most CAP lines of its output.
gh_list() {
  local name=$1 cap=$2 out
  shift 3
  if ! command -v gh >/dev/null 2>&1; then
    echo "$name: unavailable (gh is not installed)"
    return
  fi
  if ! out=$(remote "$name" gh "$@"); then
    echo "$name: unavailable (gh failed)"
    return
  fi
  print_list "$name" "$cap" "$out"
}

# print_list NAME CAP TEXT: "NAME: none" for no lines, else NAME and the first CAP lines indented.
# A CAP of 0 prints the first line on the line of NAME.
print_list() {
  local name=$1 cap=$2 text=$3 count
  if [ -z "$text" ]; then
    echo "$name: none"
    return
  fi
  if [ "$cap" -eq 0 ]; then
    echo "$name: $(printf '%s\n' "$text" | head -n 1 | cut -c1-110)"
    return
  fi
  count=$(printf '%s\n' "$text" | wc -l | tr -d ' ')
  if [ "$count" -gt "$cap" ]; then
    echo "$name (first $cap of $count):"
  else
    echo "$name:"
  fi
  printf '%s\n' "$text" | head -n "$cap" | cut -c1-110 | sed 's/^/  /'
}

JQ_ISSUE='.[] | "#\(.number) \(.title)"'
JQ_PR='.[] | "#\(.number) \(.title) (\(.headRefName))"'
JQ_WRITER='.[] | "#\(.number) \(.title) (\(.assignees | map(.login) | join(", ")))"'

echo "== Session state"
branch=$(git -C "$ROOT" branch --show-current 2>/dev/null)
changes=$(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "branch: ${branch:-none}, uncommitted: $changes"

# A live unattended run gets one line, so a session after a compaction learns
# where its clock and its rules are (ADR-0023).
if [ -f "$ROOT/build/overnight/run.json" ]; then
  (cd "$TOOLS" && "${LIMIT[@]+"${LIMIT[@]}"}" uv run --quiet python -m bodecomp.overnight \
    --root "$ROOT" hook-line) 2>/dev/null
fi

if curl -s -m 2 -o /dev/null "$URL/check_connection"; then
  echo "ghidra-mcp: up at $URL"
else
  echo "ghidra-mcp: down (start it with tools/ghidra-mcp-headless.sh)"
fi

# The stamp line reads files only, so it does not need the server (ADR-0021).
(cd "$TOOLS" && uv run --quiet python -m bodecomp.sync freshness --root "$ROOT") \
  || echo "ghidra project: unavailable (sync freshness failed)"

if command -v pgrep >/dev/null 2>&1; then
  running=""
  for entry in "ghidra-mcp server:GhidraMCPHeadlessServer" "analyzeHeadless:analyzeHeadless" "delink:tools/delink.sh"; do
    pid=$(pgrep -f "${entry#*:}" 2>/dev/null | head -n 1)
    if [ -n "$pid" ]; then
      running="${running:+$running, }${entry%%:*} (pid $pid)"
    fi
  done
  echo "running: ${running:-none}"
else
  echo "running: unavailable (pgrep is not installed)"
fi

# The ghidra-writer label is the lock on the Ghidra project (ADR-0003, ADR-0021).
if ! command -v gh >/dev/null 2>&1; then
  echo "ghidra writer: unavailable (gh is not installed)"
elif ! writers=$(remote writers gh issue list --label ghidra-writer \
  --state open --assignee '*' --json number,title,assignees --jq "$JQ_WRITER"); then
  echo "ghidra writer: unavailable (gh failed)"
elif [ -z "$writers" ]; then
  echo "ghidra writer: none"
elif [ "$(printf '%s\n' "$writers" | wc -l | tr -d ' ')" -gt 1 ]; then
  echo "WARNING: $(printf '%s\n' "$writers" | wc -l | tr -d ' ') open ghidra-writer tasks are assigned, and only one may be"
  print_list "ghidra writer" 3 "$writers"
else
  echo "ghidra writer: $writers"
fi

gh_list "open pull requests" 3 -- pr list --state open --json number,title,headRefName --jq "$JQ_PR"
gh_list "assigned issues" 3 -- issue list --assignee @me --state open --json number,title --jq "$JQ_ISSUE"

if command -v agent-skills >/dev/null 2>&1; then
  if next=$(remote next agent-skills next); then
    # Each row of the table becomes its command, so a long title never hides it.
    rows=$(printf '%s\n' "$next" | grep '^| #[0-9]' \
      | sed -E 's/^\| #[0-9]+( \(frontier\))? \|.*\| `([^`]*)` \|$/\2\1/')
    print_list "next" 4 "$rows"
  else
    echo "next: unavailable (agent-skills failed)"
  fi
else
  echo "next: unavailable (agent-skills is not installed)"
fi

gh_list "last merged pull request" 0 -- pr list --state merged --limit 1 --json number,title --jq "$JQ_ISSUE"

echo "== Open and active findings (search docs/FINDINGS.md before investigating)"
if [ -f "$ROOT/docs/FINDINGS.md" ]; then
  (cd "$TOOLS" && uv run --quiet python -m bodecomp.findings summary \
    --path "$ROOT/docs/FINDINGS.md" --limit 12) || echo "(could not read docs/FINDINGS.md)"
else
  echo "(docs/FINDINGS.md is missing)"
fi
exit 0
