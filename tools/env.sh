# Sourced by the scripts that run Ghidra. It sets GHIDRA_HOME and exports it.
#
# An existing GHIDRA_HOME wins. Otherwise the file looks for the newest Ghidra
# under the Homebrew prefix: `brew --prefix`, or when brew is not on PATH,
# $HOMEBREW_PREFIX and then /opt/homebrew. When no prefix holds
# support/analyzeHeadless, the file prints every path it tried and exits 1.
#
# The file avoids arrays because /bin/bash on macOS is version 3.2.

if [ -z "${GHIDRA_HOME:-}" ]; then
  _env_prefixes=""
  if command -v brew >/dev/null 2>&1; then
    _env_prefixes=$(brew --prefix 2>/dev/null || true)
  else
    _env_prefixes="${HOMEBREW_PREFIX:-}
/opt/homebrew"
  fi

  _env_tried=""
  while IFS= read -r _env_prefix; do
    [ -n "$_env_prefix" ] || continue
    _env_version=$(ls "$_env_prefix/Cellar/ghidra" 2>/dev/null | sort -V | tail -n 1 || true)
    _env_candidate="$_env_prefix/Cellar/ghidra/${_env_version:-<version>}/libexec"
    _env_tried="$_env_tried  $_env_candidate/support/analyzeHeadless
"
    if [ -n "$_env_version" ] && [ -x "$_env_candidate/support/analyzeHeadless" ]; then
      GHIDRA_HOME=$_env_candidate
      break
    fi
  done <<EOF
$_env_prefixes
EOF

  if [ -z "${GHIDRA_HOME:-}" ]; then
    {
      echo "Ghidra not found. Set GHIDRA_HOME, or install it with Homebrew."
      echo "Tried:"
      if [ -n "$_env_tried" ]; then
        printf '%s' "$_env_tried"
      else
        echo "  (no Homebrew prefix: brew is not on PATH and HOMEBREW_PREFIX is empty)"
      fi
    } >&2
    exit 1
  fi
  unset _env_prefixes _env_prefix _env_version _env_candidate _env_tried
fi
export GHIDRA_HOME

# The maximum Java heap of every headless Ghidra run. support/analyzeHeadless
# reads this variable and uses 2G without it, and tools/ghidra-mcp-headless.sh
# passes it to java as -Xmx. A value that is already set wins.
GHIDRA_HEADLESS_MAXMEM=${GHIDRA_HEADLESS_MAXMEM:-16G}
export GHIDRA_HEADLESS_MAXMEM
