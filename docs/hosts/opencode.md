# OpenCode integration

OpenCode is detected by the `opencode` executable. Its user-scoped configuration
is `~/.config/opencode/opencode.json`.

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

## Why the earlier plugin shapes failed (measured)

The plugin never loaded, so nothing intercepted native tools. Three shapes were
tried and each failed at a different layer on OpenCode `v2.1.4`:

| Declared shape | Host result |
| --- | --- |
| npm package `opencode-simplicio` | `failed to load plugin … 404 registry.npmjs.org/opencode-simplicio` |
| bare local file `~/.simplicio/hooks/opencode-simplicio.js` | `configured plugin path must be a directory` |
| directory with a V1 async-function export | `Plugin must export a default definition with an id and an effect or setup function` |

A configuration round trip cannot see any of these failures. Only the host
loader can, which is why `verify` below probes the plugin instead of matching
strings in JSON.

## Managed plugin and enforcement

The manifest declares the managed directory
`~/.simplicio/hooks/opencode-simplicio`, and the installer registers that
absolute path under the V2 `plugins` key. The directory contains `index.js` and
a `package.json` with `"type": "module"`.

The module default-exports `{ id: "simplicio", setup }` (`opencode-v2`) and keeps
a `server()` fallback for V1 hosts. `setup` registers `execute.before`, which
rejects host-native programming tools and directs the agent to the governed
surface:

| Native tool | Required tool |
| --- | --- |
| `read`, `read_file`, `grep`, `glob`, `list` | `simplicio_file` |
| `write`, `write_file`, `edit`, `edit_file`, `multiedit`, `patch`, `apply_patch` | `simplicio_edit` |
| `shell`, `bash`, `exec` | `simplicio_exec` |

The rejection is an actionable error, so the native tool does not run: the agent
must orient with `simplicio_map`/`simplicio_context` and retry through the
managed tool. Governed writes return a `simplicio.effect-receipt/v1` with a
`write_set`. The hook only matches native tool names. Third-party MCP servers,
their tools and unrelated OpenCode plugins remain available and untouched.

The managed `turn.before` hook warms context with `simplicio map` and the
`turn.after` hook records savings with `simplicio savings`. Both remain
advisory; enforcement comes from the plugin's `execute.before` hook.

## Install and repair

Both paths are supported:

```text
simplicio integrate install --host opencode --json
simplicio integrate verify --host opencode --json

python3 scripts/opencode_plugin.py install --json
python3 scripts/opencode_plugin.py verify --json
```

The public `scripts/opencode_plugin.py` installer writes the managed plugin
directory, replaces legacy npm and bare-file references, and preserves every
unrelated plugin, MCP server, prompt and setting. Re-running it is idempotent
and keeps a `.simplicio.bak` recovery copy. `verify` is read-only and exits
non-zero unless all of the following hold:

1. the config declares the managed directory;
2. the directory contains `index.js` and `package.json`;
3. the default export has `id: "simplicio"` and a `setup` function;
4. `setup` registers `execute.before`;
5. that hook rejects `read`, `write`, `edit` and `shell` and does not reject
   `simplicio_*` or third-party tool names;
6. the managed `mcp.simplicio` entry is still present.

The JSON verdict (`simplicio.opencode-verify/v1`) reports
`plugin.resolved`, `plugin.sha256`, `plugin.hook.verified` (`dynamic` when Node
is available) and the exact blocked/passthrough sets. The report also embeds
`runtime_integrate`, the output of `simplicio integrate verify --host opencode`,
for correlation; that Runtime check still validates the retired file/npm shape,
so the public probe above is the authoritative gate until Runtime adopts the
directory contract.

Use `--dry-run` to preview the write set or `SIMPLICIO_SKIP_OPENCODE=1` to opt
out. No provider credentials or prompt content are written by the adapter.

## Automated host proof

```text
node tests/node/opencode_host_harness.mjs contract --plugin plugins/simplicio/opencode
node tests/node/opencode_host_harness.mjs html --plugin plugins/simplicio/opencode \
  --repo <temp-repo> --binary ~/.simplicio/bin/simplicio
python3 -m pytest tests/test_opencode_plugin_enforcement.py -q
```

The harness loads the plugin the way OpenCode V2 does, captures the registered
hook, and proves native tools are rejected. The `html` scenario delivers a
native `write` for `index.html` (rejected, no file), performs the governed
`simplicio_edit` over a real MCP stdio session, and asserts the receipt's
`write_set` contains `index.html`. When the `opencode` binary is installed, the
pytest suite also boots it with an isolated config and requires a `loading
plugin` line with no `failed to load plugin`.

## Acceptance remains the final gate

Configuration and `verify` evidence only prove what was written and that the
hook rejects in a host harness. After installing and reloading OpenCode, the
final gate is one real session that shows:

1. a native `write`, `edit` or `shell` request is rejected before execution,
   with no file change and no command run, and the agent retries with
   `simplicio_edit` or `simplicio_exec`;
2. a `simplicio_*` call completes and returns its Runtime receipt; and
3. a third-party MCP tool still executes, proving the hook is scoped to native
   tools only.

Record the OpenCode version, Runtime version, provider, model, upstream
revision and receipts separately from installation evidence. A tool
registration or a prompt mention is not proof that a session used Simplicio.
