# Cursor integration

Cursor is detected only by the exact `cursor` executable. The installer
supports explicit user and workspace scopes:

- user: `~/.cursor/mcp.json`
- workspace: `.cursor/mcp.json` in the selected workspace

Each scope is independent. Existing MCP entries remain intact, the managed
entry is written atomically with a recoverable backup, and a second run is
idempotent. Discovery does not launch Cursor or infer a contract from another
editor's executable.

Use `--scope user` or `--scope workspace` (or
`SIMPLICIO_HOST_SCOPE`) to make the target explicit. `--dry-run` and
`SIMPLICIO_SKIP_CURSOR=1` provide safe preview and opt-out behavior.

Cursor can also consume the portable Agent Plugins v1 package at
`plugins/simplicio` through its own plugin/extension channel. The package ships
`plugin.json`, `mcp.json` and the shared skills; Runtime-owned MCP registration
still comes from `simplicio mcp register --binary ~/.simplicio/bin/simplicio --json`.
