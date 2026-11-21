# Simplicio with Muse Code

Muse Code is Meta's terminal coding agent. You start it with the `muse` command. It is closed source. It is not the cloud Muse app, which is a different harness. Muse Code reads MCP servers from an `mcpServers` object in `~/.config/muse/settings.json`, and from `.mcp.json` files in a trusted workspace.

Needs a Simplicio Runtime that lists `muse-code` in `simplicio integrate list`.

## What Simplicio does

- `simplicio integrate install --host muse-code` writes `mcpServers.simplicio` in `~/.config/muse/settings.json`, under your home folder. The product's user config may also be `$XDG_CONFIG_HOME/muse/settings.json`; if `XDG_CONFIG_HOME` is set, `simplicio mcp register` leaves Muse Code alone, and you put the entry there yourself (`simplicio integrations routes muse-code` prints it).
- Use the user scope. Muse Code reads project servers from a `.mcp.json` file in a trusted workspace, and the Runtime does not write that file.
- Muse Code needs `"schema_version": 1` in the file, or every command fails. The Runtime adds that key only to a file it creates. It never adds or changes it in a file that exists.
- `simplicio mcp register` writes the same entry when `~/.config/muse` exists or the `muse` command is on `PATH`.
- A file that does not parse is refused and left byte for byte as it was; nothing is written.
- An existing `simplicio` entry is replaced, not added to. Other servers and settings keep their values (the file is written back as pretty-printed JSON).
- A second run changes nothing.
- `simplicio integrate uninstall --host muse-code` removes only the `simplicio` entry. A `schema_version` the Runtime added to a file it created stays.

## Steps

1. Check that the Runtime lists the harness:

   ```
   simplicio integrate list
   ```

2. Write the entry to the user settings file:

   ```
   simplicio integrate install --host muse-code
   ```

3. Optional. Print the entry the Runtime writes:

   ```
   simplicio integrations routes muse-code
   ```

This is the entry as `integrations routes` prints it, with `schema_version` for a new file. `<path to simplicio>` stands for the path of the `simplicio` binary:

```json
{
  "mcpServers": {
    "simplicio": {
      "command": "<path to simplicio>",
      "args": ["serve", "--mcp", "--stdio", "--no-facade-mode"],
      "env": {
        "SIMPLICIO_MCP_PROFILE": "full",
        "SIMPLICIO_MCP_URL": "http://127.0.0.1:8787/mcp",
        "SIMPLICIO_MCP_HOST": "muse-code"
      }
    }
  },
  "schema_version": 1
}
```

In a file that already exists, keep your own `schema_version`. If the file has none, add `"schema_version": 1` yourself. The Runtime does not add it.

The key is `mcpServers`. The sources disagree on this spelling. See Not verified.

Last, check the install:

```
simplicio integrate verify --host muse-code
```

`simplicio integrate verify --host muse-code` reads the file the Runtime wrote and looks for the Simplicio
entry. It does not start Muse Code or make a tool call.

## What to expect

- MCP tools go through the normal approval flow. Under on-request approvals, a tool whose server declares it read-only runs without a prompt. In the build measured on 2026-11-21, 8 of Simplicio's 22 tools carry the read-only hint.
- Start-up waits 30 seconds by default (`startup_timeout_sec`). A tool call waits 300 seconds by default (`tool_timeout_sec`).
- In a stand-in test, Simplicio answered the start-up handshake in 23 to 35 ms (single samples). That was not run with Muse Code.
- A stdio server starts with a cleared environment. It keeps only `HOME`, `PATH`, `USER`, `LOGNAME`, `TMPDIR`, `TEMP`, `TMP`, `SHELL`, `LANG`, `LC_ALL` and `TERM`. It also gets the entry's `env` and `MUSE_SESSION_ID`.
- `${VAR}` and `${VAR:-default}` expand only in the `env` values of a stdio entry. They do not expand in `command`, `args`, `url` or `headers`.
- Tool names have the form `mcp__<server>__<tool>`, for example `mcp__simplicio__simplicio_map`.
- The HTTP form of the Simplicio server is not what the Runtime writes. Muse Code does not expand `${VAR}` in `headers`, so a bearer token would have to be stored in the file as plain text.
- In an untrusted workspace, no project MCP servers start.
- `enabled_tools` and `disabled_tools` are accepted but not acted on in version 1.3.0.
- MCP is not sandboxed.

## Not verified

Every item below is UNVERIFIED.
The entry was written from the product's documentation or source and was not run against a real installation of the product.

- The client name sent at initialize.
- SSE support. The docs do not describe it.
- The exact flags of `muse mcp add` for stdio.
- The key name. The official docs page shows the legacy spelling `mcp_servers`, with `transport` and `mode`. A third-party test of version 1.3.0 says only `mcpServers` works. The SDK docs say both are accepted. The Runtime writes `mcpServers`.
- The default of `required`. The SDK docs for 1.3.0 say false. A user manual page, given without a link in the study, says the legacy `mode` defaults to "required".
- The behavior of version 1.4.x beyond the changelog. The SDK docs cover 1.3.0.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://dev.meta.ai/docs/muse-code/extending
- https://meta-models.github.io/muse-code-sdk/next/guides/extend/mcp-servers/
- https://meta-models.github.io/muse-code-sdk/
- https://dev.meta.ai/docs/muse-code/changelog
- https://clickhouse.github.io/loom/features/integrations/mcp-clients/ (third party; tested on 1.4.20)
- https://www.vibecoding.cz/cheat-sheet/muse-code/ (third party; checked against 1.4.18)
- https://cyberine.dev/docs/providers/muse-cli/ (third party)
</content>
