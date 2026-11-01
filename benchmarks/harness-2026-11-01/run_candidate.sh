#!/usr/bin/env bash
# MCP server from a local Runtime build under test: SIMPLICIO_CANDIDATE_BIN names the release binary.
# Same isolation as sandbox-simplicio-mcp/run.sh: its own HOME, the host's single login file.
set -euo pipefail
bin="${SIMPLICIO_CANDIDATE_BIN:?set SIMPLICIO_CANDIDATE_BIN to the candidate binary}"
base="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/candidate-home"
mkdir -p "$base"
export SIMPLICIO_AUTH_FILE="$HOME/.simplicio/login.json"
export HOME="$base"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"
unset SIMPLICIO_MCP_PROFILE SIMPLICIO_RUNTIME_MODE SIMPLICIO_PROMPT_DELIVERY_STATE_FILE
export SIMPLICIO_DISABLE_AUTO_UPDATE=1
export SIMPLICIO_DAEMON_EXEC=0
export SIMPLICIO_TOKIO_DAEMON=0
exec "$bin" serve --mcp --stdio
