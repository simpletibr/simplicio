# OpenCode integration

OpenCode is detected by the `opencode` executable. Its user-scoped MCP
configuration is `~/.config/opencode/opencode.json`.

## Full mode

OpenCode is a **native-plugin** host running in **full mode**
(`SIMPLICIO_RUNTIME_MODE=full`), enabling the complete suite of Simplicio tools:

- `simplicio_map` & `simplicio_context` (bounded repository orientation)
- `simplicio_file`, `simplicio_edit` & `simplicio_run` (governed reads, edits and
  test execution)
- `simplicio_memory` & `simplicio_savings` (persistent context and token savings
  tracking)

Runtime registers its MCP server under the managed `mcp.simplicio` key and
preserves unrelated MCP entries, plugins, prompts and settings.

## Managed plugin and enforcement

The public manifest declares the managed local file
`~/.simplicio/hooks/opencode-simplicio.js`. The Runtime installer writes that
file and registers its absolute path, replacing the legacy npm package name
`opencode-simplicio`, which never resolved and returned 404.

The file exports a `tool.execute.before` hook. Before a native tool executes,
the hook rejects host-native programming tools and directs the agent to the
governed surface:

| Native tool | Required tool |
| --- | --- |
| `read`, `read_file`, `grep`, `glob`, `list` | `simplicio_file` |
| `write`, `write_file`, `edit`, `edit_file` | `simplicio_edit` |
| `shell`, `bash`, `exec` | `simplicio_exec` |

The rejection is an actionable error, so the native tool does not run: the
agent must map with `simplicio_map`/`simplicio_context` and retry through the
managed tool. The hook only matches native tool names. Third-party MCP servers,
their tools and unrelated OpenCode plugins remain available and untouched.

The managed `turn.before` hook warms context with `simplicio map` and the
`turn.after` hook records savings with `simplicio savings`. Both remain
advisory; enforcement comes from the plugin's `tool.execute.before` hook.

## Install and repair

Run the host integration command with the installed Runtime executable:

```text
simplicio integrate install --host opencode --json
simplicio integrate verify --host opencode --json
```

Setup merges the managed `mcp.simplicio` entry and the `plugin` array, writes
`~/.simplicio/hooks/opencode-simplicio.js` plus the turn hook scripts, and
verifies the round trip. The merge preserves unrelated JSON, rewrites the
managed declarations atomically and keeps a recovery backup. Re-running setup
repairs an older npm reference by replacing it with the managed local path.

`integrate verify --host opencode` is the config-level check. It confirms the
managed environment, the plugin path in `opencode.json`, the turn hooks and the
plugin file itself, including that the file contains `tool.execute.before`.
Verification reads the configuration and file; it does not start an OpenCode
session.

Use `--dry-run` to preview the change or `SIMPLICIO_SKIP_OPENCODE=1` to opt out.
No provider credentials or prompt content are written by the adapter.

## Acceptance remains the final gate

Installed OpenCode acceptance is not claimed by this repository. Configuration
and `integrate verify` evidence only prove what was written. After installing
and restarting OpenCode, the final gate is one real session that shows:

1. a native `write`, `edit` or `shell` request is rejected before execution,
   with no file change and no command run, and the agent retries with
   `simplicio_edit` or `simplicio_exec`;
2. a `simplicio_*` call completes and returns its Runtime receipt; and
3. a third-party MCP tool still executes, proving the hook is scoped to native
   tools only.

Record the OpenCode version, Runtime version, provider, model, upstream
revision and receipts separately from installation evidence. A tool
registration or a prompt mention is not proof that a session used Simplicio.
