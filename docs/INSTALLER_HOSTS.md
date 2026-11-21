# Installer host registration

The public shell, PowerShell and PyPI installers delegate MCP configuration to
the downloaded Runtime. The expanded adapters ship in the signed
[Runtime v3.8.50 release](https://github.com/simpletibr/simplicio/releases/tag/v3.8.50)
and are available through the public shell, PowerShell and PyPI installers.
Devin and Codebuff retain the manual integration requirements documented below.

## Additional user configuration paths

| Host | Default path | Upstream contract |
|---|---|---|
| Command Code | `~/.commandcode/mcp.json` | [Documentation](https://commandcode.ai/docs/settings) |
| xAI Grok Build | `~/.grok/settings.json`, the entry the Runtime wrote for it; the file Grok Build documents is `~/.grok/config.toml` (see below) | [Documentation](https://docs.x.ai/build/features/mcp-servers) |
| MiMo Code | `~/.config/mimocode/mimocode.json` | [Documentation](https://github.com/XiaomiMiMo/MiMo-Code) |
| Amp | `~/.config/amp/settings.json` | [Documentation](https://ampcode.com/docs/customize/mcp) |
| OpenClaude | `~/.openclaude.json` | [Documentation](https://github.com/Gitlawb/openclaude) |
| oh-my-pi | `~/.omp/agent/mcp.json` | [Documentation](https://github.com/can1357/oh-my-pi) |
| Goose | `~/.config/goose/config.yaml` | [Documentation](https://block.github.io/goose/docs/guides/config-files/) |
| Auggie | `~/.augment/settings.json` | [Documentation](https://docs.augmentcode.com/cli/integrations) |
| Autohand Code | `~/.autohand/config.json` | [Documentation](https://github.com/autohandai/code-cli/blob/main/docs/config-reference.md) |
| Charm / Crush | `~/.config/crush/crush.json` | [Documentation](https://github.com/charmbracelet/crush) |
| Continue IDE | `~/.continue/mcpServers/simplicio.yaml` | [Documentation](https://docs.continue.dev/customize/mcp-tools) |
| Droid | `~/.factory/mcp.json` | [Documentation](https://docs.factory.ai/harness/connectors) |
| Kilo Code CLI | `~/.config/kilo/kilo.json` | [Documentation](https://kilo.ai/docs/automate/mcp/using-in-cli) |
| Kimi | `~/.kimi/mcp.json` | [Documentation](https://moonshotai.github.io/kimi-cli/en/customization/mcp.html) |
| Mistral Vibe | `~/.vibe/config.toml` | [Documentation](https://docs.mistral.ai/vibe/code/cli/mcp-servers) |
| Qwen Code | `~/.qwen/settings.json` | [Documentation](https://qwenlm.github.io/qwen-code-docs/en/users/features/mcp/) |
| Rovo Dev CLI | `~/.rovodev/mcp.json` | [Documentation](https://support.atlassian.com/rovo/docs/connect-to-an-mcp-server-in-rovo-dev-cli/) |
| Pi | `~/.pi/agent/extensions/simplicio.ts` | [Documentation](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md) |
| Codex | `~/.codex/config.toml` | [Documentation](https://developers.openai.com/codex/mcp/) |

Goose on Windows uses `%APPDATA%/Block/goose/config/config.yaml`.
The native planner uses the detected initialized configuration directory.
It never launches a host during planning. Registration uses the existing
transactional writer and returns per-file receipts.

## Harnesses of the Runtime bot study

On 2026-11-21 the Runtime studied twelve harnesses: xAI Grok Build, Meta Muse
Code, OpenMausBot, OpenMuse, T3 Code, CopilotKit OpenDots, CopilotKit OpenBot,
agentes.chat, OpenAI dots, xAI Grok Bot, the Meta Muse app and Cue by Manus.
Each needs a Simplicio Runtime that lists its id in `simplicio integrate list`;
an older Runtime download does not gain it from this page. Nothing was run against
a real installation of any of these products. Every file below was written from
the vendor's documentation or from reading the package, and the Runtime prints
what it could not verify. Each product has a page in [`hosts/`](hosts/).

Earlier public text described the id `grok` as the Superagent CLI. It is xAI
Grok Build, which reads `[mcp_servers.<name>]` tables from `~/.grok/config.toml`;
the `~/.grok/settings.json` entry of the first table is not in its
documentation (UNVERIFIED), and the Runtime still writes it in the same form beside
the table.

### Files the Runtime writes

| Host (id) | Command | Default path | What is written | Upstream contract |
|---|---|---|---|---|
| [xAI Grok Build](hosts/grok.md) (`grok`) | `grok` | `~/.grok/config.toml` (project scope: `.grok/config.toml`) | a marked `[mcp_servers.simplicio]` table; `integrate` also keeps writing the `~/.grok/settings.json` entry as before | [Documentation](https://docs.x.ai/build/features/mcp-servers) |
| [Meta Muse Code](hosts/muse-code.md) (`muse-code`) | `muse` | `~/.config/muse/settings.json` | `mcpServers.simplicio`; `"schema_version": 1` only in a file the Runtime creates | [Documentation](https://dev.meta.ai/docs/muse-code/extending) |
| [OpenMausBot](hosts/openmausbot.md) (`openmausbot`) | `openmausbot` | `~/.openmausbot/config.json` | `mcpServers.simplicio` with `command`, `args`, `env` and `"resultBudget": 0` | [Documentation](https://raw.githubusercontent.com/milind-soni/OpenMausBot/main/docs/custom-mcp-servers.md) |
| [OpenMuse](hosts/openmuse.md) (`openmuse`) | `openmuse` | `~/.openmuse/config.toml` (project scope: only an existing OpenMuse `config/config.toml`) | a marked `[[mcp.servers]]` entry | [Documentation](https://github.com/OpenMuseAgent/OpenMuse/) |

For these four the Runtime refuses a file that does not parse and leaves it
byte for byte as it was, replaces an older entry of its own instead of adding
one, changes nothing on a second run, and removes only its own entry on
uninstall. `simplicio mcp register` writes them when the product's folder or
command is found; it leaves the product alone when `GROK_HOME`,
`XDG_CONFIG_HOME` (Muse Code), `OMB_DATA_DIR` (OpenMausBot) or
`OPENMUSE_CONFIG` moves its configuration. The public Python helpers never
write these files themselves.

### Nothing is written

The Runtime writes no file for these eight. `simplicio integrate install --host
<id>` answers `nothing_written` and names `simplicio integrations routes <id>`,
which prints the steps, or the documented way and what is not verified.
`simplicio integrate verify --host <id>` cannot see a connection made in a
product's own screen and says so.

| Host (id) | Kind | What the route prints |
|---|---|---|
| [CopilotKit OpenDots](hosts/opendots.md) (`opendots`) | takes a streamable-HTTP address in its own screen | the loopback endpoint, `simplicio serve --http`, the token file and the product's step |
| [CopilotKit OpenBot](hosts/openbot.md) (`openbot`) | takes an address in its own screen | the same, with `OPENBOT_ALLOW_LOOPBACK_MCP=1` |
| [agentes.chat](hosts/agentes-chat.md) (`agentes-chat`) | takes a connector URL, reachable only from a self-hosted instance | the same |
| [OpenAI dots](hosts/dots.md) (`dots`) | cloud bot, remote servers only | OpenAI's tunnel client around the stdio command |
| [xAI Grok Bot](hosts/grok-bot.md) (`grok-bot`) | cloud bot, remote servers only | a public HTTPS address you provide, and a warning about tunnels |
| [Meta Muse app](hosts/muse.md) (`muse`) | cloud app, remote servers only | the same |
| [Cue by Manus](hosts/cue.md) (`cue`) | cloud app, remote servers only | what is known, and the Manus way |
| [T3 Code](hosts/t3-code.md) (`t3-code`) | runs other agents that read their own configuration | nothing to connect; `simplicio integrate verify --host t3-code` reports, for nine agents, whether Simplicio is registered |

## Verification

1. Install or initialize the client and run the Simplicio installer.
2. Inspect `simplicio mcp register --dry-run --binary <absolute-path> --json`.
3. Apply with `simplicio mcp register --binary <absolute-path> --json`.
4. Restart/reload the host. In Pi use `/reload`.
5. Confirm the client lists Simplicio tools, then make one read-only
   `simplicio_map` call in a test repository.

The PyPI receipt accepts Runtime `writes` entries with `done` or idempotent
`skipped` status, without confusing dry-run plans with completed registration.
Invalid files, JSONC and explicit custom config paths are preserved and reported.
A user's explicit disabled state stays disabled; registration does not override
the host's permission or trust prompts.

## Clients without a user MCP registry

- **Devin:** use [Devin MCP settings](https://docs.devin.ai/work-with-devin/mcp)
  in the environment where Devin executes. Install Simplicio there and configure
  a stdio server whose command is that environment's absolute binary path with
  arguments `serve --mcp --stdio`. Local desktop paths do not refer to Devin's
  cloud filesystem; organization authorization remains Devin-owned.
- **Codebuff:** use its [custom tools SDK](https://www.codebuff.com/docs/advanced/sdk)
  in a project integration. A global `~/.codebuff/mcp.json` contract was not
  verified. The installer reports this requirement rather than claiming success.

## Maintainer validation

Runtime adapter fixtures cover JSON/YAML/TOML parsing, Windows command paths,
unrelated server preservation, idempotence and malformed/custom configuration.
The Pi extension tests exercise MCP initialization, tool discovery, calls,
shutdown, failure handling and concurrent stdio responses.
These tests do not establish live acceptance by every third-party client.
