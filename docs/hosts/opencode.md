# OpenCode integration

OpenCode is detected by the `opencode` executable. Its user-scoped MCP configuration is `~/.config/opencode/opencode.json`.

## Full mode & `opencode-simplicio` extension

OpenCode runs in **full mode** (`SIMPLICIO_RUNTIME_MODE=full`, `SIMPLICIO_MCP_PROFILE=full`), enabling the complete suite of Simplicio tools:
- `simplicio_map` & `simplicio_context` (bounded repository orientation)
- `simplicio_edit` & `simplicio_run` (governed code modifications and test execution)
- `simplicio_memory` & `simplicio_savings` (persistent context and token savings tracking)

For native lifecycle hook integration, install the extension [opencode-simplicio](https://github.com/Pasblinn/opencode-simplicio), which hooks into OpenCode events to warm context with `simplicio map` and track savings with `simplicio savings`.

The installer preserves unrelated JSON, writes the managed `simplicio` entry atomically, verifies the round trip, and keeps a recovery backup. Runtime handshake evidence is reported separately from this config-level proof.

Use `--dry-run` to preview the change or `SIMPLICIO_SKIP_OPENCODE=1` to opt out. No provider credentials or prompt content are written by the adapter.
