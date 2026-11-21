# Simplicio with T3 Code

T3 Code is an open-source control plane for coding agents. The Ping/T3 team makes it (GitHub organization `pingdotgg`, repository `pingdotgg/t3code`, MIT). The site t3code.org is an unofficial explainer. T3 Code runs other coding agents on the machine where it runs: Claude Code, Codex, Cursor, OpenCode, Grok Build, Antigravity, Kiro, Pi, Muse Code and any ACP agent. Each agent reads its own configuration and uses your own login.

T3 Code has no MCP settings of its own, as far as the study found. To give Simplicio to T3 Code, give it to the agents that T3 Code runs.

Needs a Simplicio Runtime that lists `t3-code` in `simplicio integrate list`.

## What Simplicio does

Simplicio writes nothing for T3 Code. The agents it runs get their entry from `simplicio mcp register`. For Grok Build and Muse Code, the study says that command writes the entry when the agent's folder or command exists.

`simplicio integrate verify --host t3-code` reads the files of the nine agents the Runtime knows, under your home folder. For each agent it reports `registered`, which says whether that agent's file holds a Simplicio entry on this machine. The `ok` field is true when at least one agent is registered. The nine agents and the file each one reads:

- `claude-code`: `~/.claude.json`
- `codex`: `~/.codex/config.toml`
- `cursor`: `~/.cursor/mcp.json`
- `opencode`: `~/.config/opencode/opencode.json` (on Windows, `AppData/Roaming/opencode/opencode.json`)
- `grok`: `~/.grok/config.toml`
- `antigravity`: `~/.gemini/config/mcp_config.json`
- `kiro`: `~/.kiro/settings/mcp.json`
- `pi`: `~/.pi/agent/extensions/simplicio.ts` (a bridge file that the installer stamps)
- `muse-code`: `~/.config/muse/settings.json`

To register one agent only, run `simplicio integrate install --host <agent>`.

## Steps

1. Run `simplicio mcp register`.
2. Run `simplicio integrate verify --host t3-code`. Check that the agent you want shows `registered` as true.
3. Start a thread in T3 Code with one of the registered agents.

## What to expect

- Claude Code: T3 Code runs your `claude` binary through the Claude Agent SDK. The study infers, from issue 12914 and third-party sources (not official docs), that Claude threads also load `~/.claude.json` MCP servers, project `.mcp.json` files and settings hooks.
- Claude Code: according to the study, Claude's docs say that an approval prompt cannot be shown in SDK sessions. So project `.mcp.json` servers load without asking.
- Codex: Codex reads `~/.codex/config.toml` under the `CODEX_HOME` that T3 Code uses. The default is `~/.codex`. The instance setting can change it.
- Codex: a project `.codex/config.toml` loads only when the project is trusted in your `config.toml`. Otherwise Codex skips it silently, and T3 Code shows no warning (open bug, issue 15140).
- Grok Build: the study says Grok (over ACP) inherits the user and compatibility MCP servers, and that T3 Code adds its own `t3-code` entry (issue 12914).
- Muse Code: reads `~/.config/muse/settings.json`. The study says it starts no project servers in an untrusted workspace.
- Cursor: the study says that under the Cursor SDK, the setting sources project, user, team, mdm and plugins stay in effect.
- Permission modes: Supervised, Auto-accept edits, Auto and Full access. The default is Full access. Each provider differs. There is no separate MCP approval setting. MCP calls follow the permission mode. Claude can still ask in Full access if its own settings require it.
- Codex sandbox: Full access means `dangerFullAccess` and approval `never` (issue 15140).
- Time limits: the study reads issue 23151 as a Claude limit of 5 minutes to start and 90 seconds for MCP registration. The study does not say whether these limits are intended or bugs.
- The server runs on the host where the agent runs. The study does not place it on a phone or a browser client.
- Desktop-launched profiles had gaps in their environment (issue 9230, closed, referenced in issue 15140).

## Not verified

Every item below is UNVERIFIED.
Nothing was run against a real T3 Code. `integrate verify --host t3-code` was not run against one either.

- The latest stable T3 Code version and date. The study saw only the nightly `0.1.12-nightly.20261121.5038`.
- Codex hooks in chat sessions.
- The Codex client name value.
- The `--mcp-config` example for Claude. It has no source.
- Claude hooks, from official docs. The study has only issue evidence.
- Whether Claude threads load `~/.claude.json`, project `.mcp.json` and settings hooks. This is an inference, as stated above.
- How third-party MCP calls are shown in T3 Code.
- The full `~/.t3` folder layout.
- Whether the issue 23151 limits are intended or bugs.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://github.com/pingdotgg/t3code/blob/main/AGENTS.md
- https://raw.githubusercontent.com/pingdotgg/t3code/main/docs/user/providers-codex.md
- https://raw.githubusercontent.com/pingdotgg/t3code/main/docs/user/providers-claude.md
- https://raw.githubusercontent.com/pingdotgg/t3code/main/docs/user/permission-modes.md
- https://github.com/pingdotgg/t3code/issues/12914
- https://github.com/pingdotgg/t3code/issues/15140
- https://github.com/pingdotgg/t3code/issues/23151
- https://code.claude.com/docs/en/mcp
