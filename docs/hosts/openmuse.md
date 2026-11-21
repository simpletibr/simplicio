# Simplicio with OpenMuse

OpenMuse is a Python agent package, installed with `pip install openmuse`. Its README says it works "in the shape of Meta's Muse". The Runtime's entry follows version 0.6.0 of that package, which the study unpacked and read on 2026-11-21. The project later moved to nano-muse/nanoMuse, which has another executable (`nanomuse`) and another config file (`~/.nanomuse/config.toml`); the Runtime writes neither. OpenMuse reads MCP servers from `[[mcp.servers]]` tables in a TOML config file, and its app can add them too.

Which OpenMuse this guide means is not settled. See Not verified.

Needs a Simplicio Runtime that lists `openmuse` in `simplicio integrate list`.

## What Simplicio does

- `simplicio integrate install --host openmuse` writes a marked `[[mcp.servers]]` entry with `name`, `command`, `args` and `env` to `~/.openmuse/config.toml`. It sets nothing else, so `risk`, `egress` and `reads_private_data` keep their defaults.
- An entry named `simplicio` found elsewhere in the file is replaced, not added to. Every other byte stays.
- A file that does not parse is refused and left byte for byte as it was. So is a file whose `mcp.servers` is a static array.
- A second run changes nothing.
- OpenMuse 0.6.0 reads the first config file it finds: `--config`, `$OPENMUSE_CONFIG`, `./config/config.toml`, then `~/.openmuse/config.toml`. It merges none of them. The nanoMuse documentation gives another order: `--config` or `NANOMUSE_CONFIG`, then `./config/config.toml`, then `~/.nanomuse/config.toml`.
- `simplicio mcp register` writes the user-scope entry when `~/.openmuse` exists or the `openmuse` command is on `PATH`. It leaves OpenMuse alone when `OPENMUSE_CONFIG` is set.
- `simplicio integrate uninstall --host openmuse` removes only the marked entry. At project scope it removes it from an existing file and creates nothing.

Project scope (`--scope project`) is different, and the Runtime is strict about it. It writes only into an existing `config/config.toml` that is OpenMuse's. It never creates that file. The source comment gives the reason. OpenMuse merges no config files, so a new `config/config.toml` with only the Simplicio entry would replace the user's `~/.openmuse/config.toml` (model, keys and all) for every run started in that folder. And `config/config.toml` is a path other programs use. A block appended to their file could break them.

A file counts as OpenMuse's when it has a top-level `sentinel` or `mcp` key, or a top-level `data_dir` string that contains `openmuse`, or when it already holds a Simplicio entry. The file that `openmuse config init` writes has `[sentinel]` and `data_dir = "~/.openmuse"`. With no project file, the install is refused and nothing is written. With another program's file, it is refused and that file is left alone. The refusals are `host_config_absent` (no project file) and `host_config_foreign` (another program's file). With `--host openmuse --scope project` the command exits 1 with the refusal. `simplicio integrate install --all --scope project` reports OpenMuse as skipped instead and exits 0 when nothing else failed.

## Steps

1. Check that the Runtime lists the harness:

   ```
   simplicio integrate list
   ```

2. Write the entry to the user config:

   ```
   simplicio integrate install --host openmuse
   ```

   For a project, first create the project file with `openmuse config init`, in the project folder. Then run `simplicio integrate install --host openmuse --scope project`.

3. Optional. Print the entry the Runtime writes:

   ```
   simplicio integrations routes openmuse
   ```

The entry looks like this. `<path to simplicio>` stands for the path of the `simplicio` binary:

```toml
# simplicio-mcp-integration: openmuse-v1
[[mcp.servers]]
name = "simplicio"
command = "<path to simplicio>"
args = ["serve", "--mcp", "--stdio", "--no-facade-mode"]
env = { SIMPLICIO_MCP_PROFILE = "full", SIMPLICIO_MCP_URL = "http://127.0.0.1:8787/mcp", SIMPLICIO_MCP_HOST = "openmuse" }
# /simplicio-mcp-integration: openmuse-v1
```

OpenMuse has no working-directory setting. The server starts in OpenMuse's own directory, so the model must pass `repo` in each Simplicio call.

Last, check the install:

```
simplicio integrate verify --host openmuse
```

`simplicio integrate verify --host openmuse` reads the file the Runtime wrote and looks for the Simplicio
entry. It does not start OpenMuse or make a tool call.

## What to expect

- Every MCP tool passes the Sentinel. It allows, asks or denies by risk level: `safe`, `moderate` or `sensitive`, set per server or per tool. The entry leaves `risk` at `moderate`. In the default mode, a call at `moderate` runs without a prompt, and only `sensitive` asks. This is from the 0.6.0 package, read and not run.
- Tool names have the form `server__tool`, cut to 64 characters: `simplicio__simplicio_map`.
- Pass `repo` in each call. A refusal's suggested next call can carry the placeholder `repo: "."`. With OpenMuse, `.` is OpenMuse's own directory. The effect on a real client was not run.
- With a non-empty `env`, the stdio child gets OpenMuse's whole environment plus the entry's variables.
- OpenMuse 0.6.0 sends no client name at initialize. The entry's `SIMPLICIO_MCP_HOST = "openmuse"` declares the host.
- OpenMuse 0.6.0 has no connect or call time-out fields. In a stand-in test, Simplicio answered the start-up handshake in 23 to 35 ms (single samples).
- Simplicio's HTTP server cannot be registered from 0.6.0. A URL entry cannot carry the `Authorization` header that `simplicio serve --http` needs (source read, not run).
- Servers added from the phone app go to `<data_dir>/app-settings.json` and replace a same-named TOML entry (0.6.0 source).
- A local server on 127.0.0.1 is reachable only when the agent runs on the same machine. It is not reachable from the phone app's sandbox (nanoMuse documentation).

## Not verified

Every item below is UNVERIFIED.
The entry was written from the product's documentation or source and was not run against a real installation of the product.

- Which OpenMuse is meant. The identification has LOW confidence. The decision of the project takes the Python package.
- MCP support in CopilotKit/openfuse (formerly CopilotKit/OpenMuse) and in diggerhq/openmuse. None was found in the sources read.
- The client name at initialize. The Python SDK default was not run.
- The default connect and call time-outs for nanoMuse. The 0.6.0 package has none.
- How a bearer token is sent in the URL form.
- The licence. Two records were found: MIT (OpenMuseAgent/OpenMuse) and GPL-3.0-or-later (nano-muse/nanoMuse). Which applies now is not settled.
- Whether the 0.6.0 parser accepts the entry the Runtime writes. This is derived from the source; nothing was run.

## Sources

- https://github.com/OpenMuseAgent/OpenMuse/
- https://github.com/nano-muse/nanoMuse
- https://nanomuse.cn
- https://nanomuse.cn/docs/architecture
- https://nanomuse.cn/docs/zh/configuration
- https://nanomuse.cn/docs/app
- https://github.com/CopilotKit/openfuse (formerly CopilotKit/OpenMuse)
- https://personalagentbench.com/openmuse/ (review)
- https://www.open-muse.dev/
- https://github.com/diggerhq/openmuse
</content>
