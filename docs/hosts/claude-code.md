# Claude Code integration

Claude Code is detected only by the exact `claude` executable. Simplicio does
not launch the host during discovery and never treats a similarly named binary
as Claude Code.

The installer writes one managed `simplicio` MCP entry to the user-scoped
`~/.claude/settings.json` file (or `~/.claude/.mcp.json` when that is the first
documented path available). Existing keys are preserved, writes are atomic,
and a `.simplicio.bak` copy is kept before a replacement. Re-running the
installer is a no-op after the entry is already correct.

The installer-scoped MCP entry sets `SIMPLICIO_RUNTIME_MODE=full` and
`SIMPLICIO_MCP_PROFILE=full`, the profile every host now registers: the whole
Runtime catalogue is advertised and Claude still owns its native editing and
terminal tools. The retired `mapper-only` profile is no longer written by the
installer, the Claude MCP bootstrap or the Hermes plugin; an entry that still
carries it resolves as unset. A registration receipt is not a live handshake.

The installer also pre-approves `mcp__simplicio__*` in
`~/.claude/settings.json` under `permissions.allow`, so a Claude Code session in
auto mode does not deny a Simplicio tool. Uninstall removes only the entry the
installer wrote.

Live MCP registration and handshake evidence remain Runtime-owned. A dry run
reports the planned path without creating or changing files; set
`SIMPLICIO_SKIP_CLAUDE_CODE=1` to opt out.

Claude Desktop registers the same `full` surfaces. `simplicio doctor`
reports any Claude or Hermes MCP/hook registration whose effective profile is
not `full` instead of silently accepting it.
