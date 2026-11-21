# Simplicio with Grok Build

Grok Build is the terminal coding agent of xAI. You start it with the `grok` command. It reads MCP servers from `[mcp_servers.<name>]` tables in `~/.grok/config.toml`, and the `grok mcp add` command can add them too.

Needs a Simplicio Runtime that lists `grok` in `simplicio integrate list`.

## What Simplicio does

- `simplicio integrate install --host grok` writes a `[mcp_servers.simplicio]` table between two marker comments in `~/.grok/config.toml`.
- With `--scope project`, it writes under the repository instead of your home folder: `.grok/config.toml` and the JSON entry below.
- It also keeps writing the `mcpServers.simplicio` entry in `.grok/settings.json` that earlier Runtime versions wrote, in the same form as before. Grok Build's documentation does not name that file (see Not verified), so the table in `config.toml` is the registration.
- `simplicio mcp register` writes the same table when `~/.grok` exists or the `grok` command is on `PATH`. It leaves Grok alone when `GROK_HOME` moves the config.
- A file that does not parse is refused and left byte for byte as it was. So is a file where `mcp_servers` is an inline table (`mcp_servers = { ... }`), which cannot take a table. A refused install writes none of its files.
- A table of Simplicio found elsewhere in the file, in an older form, is replaced, not added to. Other settings and tables keep their bytes.
- A second run changes nothing.
- `simplicio integrate uninstall --host grok` removes only the Simplicio table and the Simplicio entry in `.grok/settings.json`.

## Steps

1. Check that the Runtime lists the harness:

   ```
   simplicio integrate list
   ```

2. Write the entry to the user config:

   ```
   simplicio integrate install --host grok
   ```

   For one repository only, use `simplicio integrate install --host grok --scope project`. Grok Build reads a project config only after the folder is trusted (`--trust` or `/hooks-trust`).

3. Optional. Print the entry the Runtime writes:

   ```
   simplicio integrations routes grok
   ```

The table in `~/.grok/config.toml` looks like this. `<path to simplicio>` stands for the path of the `simplicio` binary:

```toml
# simplicio-mcp-integration: grok-v1
[mcp_servers.simplicio]
command = "<path to simplicio>"
args = ["serve", "--mcp", "--stdio", "--no-facade-mode"]
env = { SIMPLICIO_MCP_PROFILE = "full", SIMPLICIO_MCP_URL = "http://127.0.0.1:8787/mcp", SIMPLICIO_MCP_HOST = "grok" }
# /simplicio-mcp-integration: grok-v1
```

Last, check the install:

```
simplicio integrate verify --host grok
```

`simplicio integrate verify --host grok` reads the file the Runtime wrote and looks for the Simplicio
entry. It does not start Grok Build or make a tool call.
It needs the table in `config.toml`: the JSON file alone is not a registration.

## What to expect

- Grok Build asks before each tool call in its default mode. Allow and deny rules use `--allow` and `--deny`, or the `[permission]` table. The docs give this rule form: `MCPTool(sales__delete_*)` under `deny`.
- Tool names have the form `server__tool`, for example `simplicio__simplicio_map`.
- The start-up wait is 30 seconds by default (`startup_timeout_sec`). `MCP_TIMEOUT` (milliseconds) or `GROK_MCP_STARTUP_TIMEOUT_SECS` change it.
- A tool call waits 6000 seconds by default (`tool_timeout_sec`).
- Results are capped at 20,000 bytes (`[mcp] max_output_bytes`). On a 17-file test tree the largest Simplicio reply was 7,452 characters. That test used a stand-in client, not Grok Build. A larger tree was not run.
- `${VAR}` and `${VAR:-default}` expand in `url`, `command`, `args`, `env` and `headers`.
- Grok Build also reads `~/.claude.json`, `.cursor/mcp.json` and a project `.mcp.json`. Those rank below `config.toml`. `[compat.claude] mcps=false` turns off the Claude files.
- A project server with the same name replaces the user server entirely.
- An organization policy can allow or deny servers (`allowedMcpServers`, `deniedMcpServers`).
- Grok Build names its client `grok-shell-<server name>` at start-up (the source the study read).

## Not verified

Every item below is UNVERIFIED.
The entry was written from the product's documentation or source and was not run against a real installation of the product.

- `.grok/settings.json`: not in the docs. The docs name `config.toml` only.
- The `grok mcp add` flag details beyond the docs.
- Whether a stdio server needs a `type` field.
- Whether SSE is deprecated.
- Which hook events can block. The two sources disagree. The older doc says `PreToolUse` is the only blocking event. The newer guide says `UserPromptSubmit` and `Stop` can block too.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://raw.githubusercontent.com/xai-org/grok-build/main/README.md
- https://docs.x.ai/build/overview
- https://x.ai/cli
- https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-pager/docs/user-guide/07-mcp-servers.md
- https://docs.x.ai/build/features/mcp-servers
- https://docs.x.ai/build/settings
- https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-pager/docs/user-guide/22-permissions-and-safety.md
- https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-mcp/src/servers.rs (source code)
- https://docs.x.ai/build/features/hooks
- https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-pager/docs/user-guide/10-hooks.md
- https://docs.x.ai/build/features/project-rules
- https://docs.x.ai/build/features/skills-plugins-marketplaces
</content>
