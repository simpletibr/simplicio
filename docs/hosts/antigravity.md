# Google Antigravity (agy)

Google Antigravity is a supported host running on MCP profile `core` with full lifecycle pre-hooks.

## Configuration

- **MCP Configuration**: `~/.gemini/config/mcp_config.json`
  - Transport: `stdio`
  - Command: `~/.simplicio/bin/simplicio serve --mcp --stdio --no-facade-mode`
  - Profile: `SIMPLICIO_MCP_PROFILE=core`
  - Mode: `SIMPLICIO_RUNTIME_MODE=core`
- **Hooks Configuration**: `~/.gemini/config/hooks.json`
  - PreInvocation: Injects ephemeral instruction enforcing `simplicio_*` MCP tools and performs non-blocking map cache warmup.
  - PreToolUse: Intercepts and denies host-native file tools (`view_file`, `write_to_file`, `replace_file_content`), directing the agent to use `simplicio_file_read` / `simplicio_context` / `simplicio_read_signatures` and `simplicio_edit` / `simplicio_run`. Third-party apps, plugins, and non-file tools remain permitted.
  - Stop: Records savings metrics non-blockingly upon session completion.
