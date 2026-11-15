#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
GHIDRA_HOME=${GHIDRA_HOME:-/opt/homebrew/Cellar/ghidra/12.2/libexec}
MCP_DIR=${GHIDRA_MCP_DIR:-$HOME/git/bethington/ghidra-mcp}
# Ghidra keeps user extensions under $XDG_CONFIG_HOME when that is set, which is
# where the XBE loader and the delinker are installed on this machine.
EXTENSIONS=${XDG_CONFIG_HOME:-$HOME/.config}/ghidra/ghidra_12.2_PUBLIC/Extensions

# The GhidraMCP extension folder is skipped because the server jar below already
# contains the same classes, which would otherwise be on the classpath twice.
classpath="$MCP_DIR/target/GhidraMCP-7.0.0.jar"
for jar in "$GHIDRA_HOME"/Ghidra/{Framework,Features,Processors}/*/lib/*.jar; do
  classpath="$classpath:$jar"
done
for jar in "$EXTENSIONS"/*/lib/*.jar; do
  case "$jar" in */GhidraMCP/*) continue ;; esac
  classpath="$classpath:$jar"
done

exec java -Xmx4g -XX:+UseG1GC \
  -Dghidra.home="$GHIDRA_HOME" -Dapplication.name=GhidraMCP \
  -classpath "$classpath" com.xebyte.headless.GhidraMCPHeadlessServer \
  --bind 127.0.0.1 --port 8089 --project "$ROOT/ghidra/BustinOut.gpr"
