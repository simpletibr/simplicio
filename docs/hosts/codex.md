# Codex integration

Codex installs the public plugin through its native marketplace channel:

```bash
codex plugin marketplace add simpletibr/simplicio --ref master
codex plugin add simplicio@simplicio-codex
```

The plugin bootstraps the verified managed Runtime and exposes the complete
stdio MCP surface; `simplicio_exec` reaches every CLI subcommand. Start a new
Codex task after installation and authenticate explicitly with
`simplicio login google`.

The Runtime remains the binary authority: host registration is
`simplicio mcp register --binary ~/.simplicio/bin/simplicio --json`.
