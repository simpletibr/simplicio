# Simplicio with OpenMausBot

OpenMausBot is an open-source desktop app (Apache-2.0). It runs AI bots as a chat app. The bots run the `claude`, `codex` and `grok` command-line agents, ACP agents and API models. The study says it is not affiliated with xAI. It reads MCP servers from `mcpServers` in `~/.openmausbot/config.json`, or from the Add server screen under Plugins.

Needs a Simplicio Runtime that lists `openmausbot` in `simplicio integrate list`.

## What Simplicio does

- `simplicio integrate install --host openmausbot` writes `mcpServers.simplicio` in `~/.openmausbot/config.json`, under your home folder. OpenMausBot itself keeps its data in `$OMB_DATA_DIR` when that is set; then `simplicio mcp register` leaves OpenMausBot alone, and you put the entry in that folder's `config.json` yourself (`simplicio integrations routes openmausbot` prints it).
- OpenMausBot has no project config in the sources. Use the user scope.
- The entry has exactly four keys: `command`, `args`, `env` and `resultBudget`. OpenMausBot skips an entry that has any key it does not know, so the Runtime writes no other key.
- `"resultBudget": 0` turns off OpenMausBot's trimming of this server's replies. By default, OpenMausBot cuts a custom command server's reply at 8,000 characters and writes the whole text to a file.
- `simplicio mcp register` writes the same entry when `~/.openmausbot` exists or the `openmausbot` command is on `PATH`.
- A file that does not parse is refused and left byte for byte as it was; nothing is written.
- An existing `simplicio` entry is replaced, not added to. Other servers and settings keep their values (the file is written back as pretty-printed JSON).
- A second run changes nothing.
- `simplicio integrate uninstall --host openmausbot` removes only the `simplicio` entry.

## Steps

1. Check that the Runtime lists the harness:

   ```
   simplicio integrate list
   ```

2. Write the entry to the OpenMausBot config:

   ```
   simplicio integrate install --host openmausbot
   ```

3. Optional. Print the entry the Runtime writes:

   ```
   simplicio integrations routes openmausbot
   ```

The file holds this entry. `<path to simplicio>` stands for the path of the `simplicio` binary:

```json
{
  "mcpServers": {
    "simplicio": {
      "command": "<path to simplicio>",
      "args": ["serve", "--mcp", "--stdio", "--no-facade-mode"],
      "env": {
        "SIMPLICIO_MCP_PROFILE": "full",
        "SIMPLICIO_MCP_URL": "http://127.0.0.1:8787/mcp",
        "SIMPLICIO_MCP_HOST": "openmausbot"
      },
      "resultBudget": 0
    }
  }
}
```

OpenMausBot reads `config.json` again only after a restart. Restart OpenMausBot, then check the install:

```
simplicio integrate verify --host openmausbot
```

`simplicio integrate verify --host openmausbot` reads the file the Runtime wrote and looks for the Simplicio
entry. It does not start OpenMausBot or make a tool call.

## What to expect

- Custom servers are never pre-approved. Claude bots show an Allow card and a Deny card for each call.
- Adding a server in the app runs a test: a handshake and a tool listing. The test stops after the handshake or after 8 seconds.
- On a bot turn, a command server has 8 seconds to start. In a stand-in test on a 17-file tree, Simplicio answered the start-up handshake in 23 to 35 ms (single samples). That was not run with OpenMausBot.
- A command server reaches Claude Code, Codex, ACP agents and API-model bots.
- The Codex engine starts a new child process on every turn (read in the source, not run). With a stand-in client that started a new stdio server for each call, a write on a folder of more than 10 files could not be finished: the map answer carries over, the context answer and the commit id of a kept write do not. Whether this happens in OpenMausBot was not run.
- Each bot has its own MCP access limit, set in Tools > Access > MCP servers.
- Header and env values are stored in plain text in `config.json`, with file mode 0600.
- Names of `env` variables must not start with `OMB_` or `OGB_`.
- Simplicio replies are TOON text. The largest reply on the 17-file test tree was 7,452 characters. A larger tree is expected to pass 8,000 characters (an extrapolation). That is why the entry sets `resultBudget` to 0.
- OpenMausBot also ships a stdio server named `openmausbot mcp`. It controls bots. It is not Simplicio.

## Not verified

Every item below is UNVERIFIED.
The entry was written from the product's documentation or source and was not run against a real installation of the product.

- The tool-name prefix that each engine adds. For Claude, `mcp__name__tool` is UNVERIFIED.
- User-defined PreToolUse hooks. None were found.
- Whether OpenMausBot reads AGENTS.md.
- The client name on real bot turns. The `grok-shell` form is an inference.
- Whether loopback URLs are accepted.
- Whether OpenMausBot accepts the entry the Runtime writes. This is derived from the source; nothing was run.
- Start-up against the 8-second window. The series of ten starts was not run. The 23 to 35 ms figures are single samples.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://github.com/milind-soni/OpenMausBot
- https://codeberg.org/paperbyte/OpenMausBot (mirror)
- https://www.npmjs.com/package/openmausbot (package read on 2026-11-21)
- https://www.openmausbot.com
- https://www.mausbot.com
- https://raw.githubusercontent.com/milind-soni/OpenMausBot/main/docs/custom-mcp-servers.md
- https://raw.githubusercontent.com/milind-soni/OpenMausBot/main/server/mcp-probe.ts (source code)
- https://raw.githubusercontent.com/milind-soni/OpenMausBot/main/server/imported-skills.ts (source code)
- https://raw.githubusercontent.com/milind-soni/OpenMausBot/main/docs/mcp-server.md
</content>
