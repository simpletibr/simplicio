#!/usr/bin/env bash
# Simplicio MCP route — advisory Map cache for every supported host.
# simplicio-hook-version: 4128-v1
#
# #6128: this used to be a ~640-line embedded Python heredoc. The whole
# decision (Map warming, mapper-only context injection, the native-file-tool
# deny path) now lives once, in Rust, as `simplicio hooks pre-tool`
# (src/hooks_command.rs). This script is a thin, fail-soft wrapper: it reads
# the host's hook JSON on stdin, hands it to the Runtime binary unchanged,
# and forwards the binary's stdout and exit code back to the host verbatim.
#
# Same installed callers as before: the global Claude Code hook
# (`claude_code_global_hooks_plan` in src/planned_writes.rs) and the
# per-project `simplicio-pre-tool.sh` (`PRE_TOOL_SH_STRICT` in
# src/host_integrations.rs, byte-identical to this file).
set -uo pipefail

SIMPLICIO_BIN="${SIMPLICIO_BIN:-${SIMPLICIO_BIN_DIR:-${HOME}/.simplicio/bin}/simplicio}"

INPUT="$(cat 2>/dev/null || true)"
# Codex 0.150.0 rejects an explicit PreToolUse allow without updatedInput.
# Empty stdout is the portable allow-unchanged contract.
[ -n "$INPUT" ] || exit 0

# Fail soft: no Runtime binary on this host means no opinion, not a block.
if ! command -v "$SIMPLICIO_BIN" >/dev/null 2>&1; then
  exit 0
fi

printf '%s' "$INPUT" | exec "$SIMPLICIO_BIN" hooks pre-tool
