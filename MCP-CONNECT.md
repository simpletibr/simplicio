# Connecting an MCP Client to Simplicio

Simplicio exposes a local [Model Context Protocol](https://modelcontextprotocol.io/) server. The Runtime owns authentication, entitlement checks, safety gates, and the embedded Python ecosystem; an MCP client only discovers and invokes the structured tools.

## Prerequisite: Google login

Product commands and MCP require an active Simplicio session, including during the public beta:

```bash
simplicio auth login
simplicio auth status --json
```

Continue only when the status reports `active: true`. Never copy a password, device code, bearer token, refresh token, or client secret into an MCP config.

## Codex: local STDIO MCP and hooks

The installer automatically invokes the installed Runtime's host registrar.
There is no Codex opt-in flag and no separately downloaded hook. The Runtime
detects supported clients, records the absolute managed-binary path, preserves
existing user configuration, and installs native hooks only where a verified
native hook API is available.

Registration runs before login reporting, so a fresh installation is configured
even when the user has not authenticated yet. Protected MCP operations still
validate Google login and entitlement when they are used. Restart every open
client after installation so it reloads the MCP and hook files.

MCP clients launch `command` directly, so do not use `~` and do not expect
shell expansion.

#### Windows

~~~toml
[mcp_servers.simplicio]
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]

[mcp_servers.simplicio.env]
SIMPLICIO_MCP_URL = "http://127.0.0.1:8787/mcp"
~~~

Use forward slashes in Windows TOML paths.

#### macOS

~~~toml
[mcp_servers.simplicio]
command = "/Users/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]

[mcp_servers.simplicio.env]
SIMPLICIO_MCP_URL = "http://127.0.0.1:8787/mcp"
~~~

#### Linux

~~~toml
[mcp_servers.simplicio]
command = "/home/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]

[mcp_servers.simplicio.env]
SIMPLICIO_MCP_URL = "http://127.0.0.1:8787/mcp"
~~~

STDIO is the primary local transport. The Runtime's JSON registration report
lists every client it detected and whether the MCP configuration or native hook
was written. A failed write makes installation fail rather than silently
continuing.

To inspect or repair the detected integrations:

~~~bash
simplicio mcp register --binary "$(command -v simplicio)" --json
~~~

Restart Codex and other open clients after registration. Never paste tokens into
client configuration files.

## Other clients: local STDIO

Add this server entry to any MCP-compatible client that supports STDIO:

```json
{
  "mcpServers": {
    "simplicio": {
      "command": "/absolute/path/to/.simplicio/bin/simplicio",
      "args": ["serve", "--mcp", "--stdio"]
    }
  }
}
```

Common locations:

| Client | File |
|---|---|
| Claude Code | `~/.claude.json` (user/local) or project `.mcp.json` |
| Cursor | `~/.cursor/mcp.json` |
| VS Code | `.vscode/mcp.json` |
| Cline | `~/.config/cline/mcp_settings.json` |
| Continue | `~/.continue/config.json` |

Replace the placeholder with the installed binary's absolute path. Claude Code plugin-provided servers follow the plugin lifecycle; do not copy them into project configuration unless the host requires it. Reload the client after editing its configuration. STDIO does not require a manually copied bearer token, but the local Runtime still requires the Google login above.

## The project Map arrives without a call

The `initialize` instructions carry a structural header — manifests, entry
files, two directory levels, the flow line and the registry categories — and a
session-start hook appends the Map body once per session. A host is oriented
before its first tool call; call `simplicio_map` when a specific question needs a
fresh generation, not to establish the project at all.

## Tools

The public CLI/MCP vocabulary is `simplicio map`, `simplicio context`,
`simplicio memory`, `simplicio edit`, and `simplicio run`. Mapper observes,
Fast projects or retrieves, Dev CLI edits, Runtime governs, and Loop
converges. Every host registers `SIMPLICIO_MCP_PROFILE=full`, so Claude and
Hermes advertise the same full surface as every other host; the retired
`mapper-only` profile no longer exists. `SIMPLICIO_MCP_PROFILE=exec` narrows the
list to six tools: `simplicio_context`, `simplicio_edit`, `simplicio_run`,
`simplicio_exec`, `simplicio_codegen` and `simplicio_tools_unlock`.
Deprecated aliases (`mapper`, `index`, `code-graph`, `mapper-memory`) must
not appear as a second MCP tool. A Runtime below the unified-surface
minimum must not advertise the new names.

MCP calls run on the resident daemon, which is on by default
(`SIMPLICIO_TOKIO_DAEMON=0` disables it).

`tools/list` is the live authority. A full-profile Runtime lists the whole
catalogue — 22 tools — plus the tools of the installed plugins (34 from the
fifteen packaged plugins, 56 in total on a machine that has them all). The core
of that list is:

| Tool | Purpose |
|---|---|
| `simplicio_map` | Compact structural repository map (`simplicio map`) |
| `simplicio_context` | Bounded task context (`simplicio context`) |
| `simplicio_memory` | Indexed project-memory recall (`simplicio memory`) |
| `simplicio_edit` | Structured deterministic file edits (`simplicio edit`) |
| `simplicio_run` | Governed task execution (`simplicio run`) |
| `simplicio_validate` | Deterministic pipeline, test and delivery-gate checks |
| `simplicio_file` | Read-only bounded workspace reads: ls, grep, signatures, diff |
| `simplicio_codegen` | Generator operations: build, generate, fill, sync, infer |
| `simplicio_exec` | Supervised external commands |
| `simplicio_plan` | Admitted work plans, Loop decisions and routing |
| `simplicio_doctor` | Runtime health, readiness and opt-in repair |
| `simplicio_report` | Execution reports, savings events and activity |

Always discover the live schemas at startup instead of hard-coding arguments:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  | ~/.simplicio/bin/simplicio serve --mcp --stdio
```

A successful response contains the tool definitions. A `login required` error means the account session is not active; authenticate instead of bypassing the gate.

## Automatic setup

The official PyPI bootstrap verifies the binary checksum, Ed25519 signature,
and release-manifest contract, then requires active login. Codex MCP registration
and routing hooks are registered by the installer for supported hosts;
review the JSON receipt and any requested consent before relying on the integration.
The installer writes `SIMPLICIO_MCP_PROFILE=full` for every host and pre-approves
`mcp__simplicio__*` in Claude Code's `permissions.allow`; the Gemini entry is
written with `trust: true`. A host in auto mode therefore does not deny a
Simplicio tool, and uninstall removes only the entry the installer wrote.
Other MCP clients can use the local STDIO entry above without copying tokens.

A quick PyPI bootstrap is:
~~~bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
~~~

For the full installation, update, benchmark, and troubleshooting guide, see [`README.md`](README.md).
