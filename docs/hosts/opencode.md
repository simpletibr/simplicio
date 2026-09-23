# OpenCode integration

OpenCode is detected by the `opencode` executable. Its user-scoped MCP configuration is `~/.config/opencode/opencode.json`.

## Full mode & `opencode-simplicio` extension

OpenCode is a **native-plugin** host running in **full mode** (`SIMPLICIO_RUNTIME_MODE=full`, `SIMPLICIO_MCP_PROFILE=full`), enabling the complete suite of Simplicio tools:
- `simplicio_map` & `simplicio_context` (bounded repository orientation)
- `simplicio_edit` & `simplicio_run` (governed code modifications and test execution)
- `simplicio_memory` & `simplicio_savings` (persistent context and token savings tracking)

For native lifecycle hook integration, install the extension [opencode-simplicio](https://github.com/Pasblinn/opencode-simplicio), which hooks into OpenCode events to warm context with `simplicio map` and track savings with `simplicio savings`.

Setup flow:
1. Install the extension in OpenCode (`plugin` array in `opencode.json` includes `opencode-simplicio`).
2. Register Simplicio Runtime MCP (`simplicio mcp register`) which writes the managed `mcp.simplicio` entry with `SIMPLICIO_RUNTIME_MODE=full`.
3. Runtime also writes managed `turn.before` / `turn.after` hooks and the extension scripts under `~/.simplicio/hooks/`.
4. Restart OpenCode so the plugin and hooks load.

The installer preserves unrelated JSON, writes the managed `simplicio` entry atomically, verifies the round trip, and keeps a recovery backup. Runtime handshake evidence is reported separately from this config-level proof.

Use `--dry-run` to preview the change or `SIMPLICIO_SKIP_OPENCODE=1` to opt out. No provider credentials or prompt content are written by the adapter.
