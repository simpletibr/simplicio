# Compatibility matrix

The installer exposes this matrix through `compatibility_matrix()` and keeps
every row explicit. Detection is exact and non-invasive; `unsupported` rows
have no guessed executable and no automatic configuration writer.

| Host | Capability | Contract | Probe |
| --- | --- | --- | --- |
| Claude Code | runtime-mcp | delegated-to-runtime | `claude` |
| Cursor | runtime-mcp | delegated-to-runtime | `cursor` |
| DeepSeek Harness | unsupported | unverified | — |
| OpenCode | native-plugin | delegated-to-runtime | `opencode` |
| Visual Studio Code | runtime-mcp | delegated-to-runtime | `code`, `code-insiders` |
| Google Antigravity | unsupported | unverified | — |
| Kiro | runtime-mcp | delegated-to-runtime | `kiro-cli` |
| Pi | runtime-mcp | delegated-to-runtime | `pi` |
| oh-my-pi | runtime-mcp | delegated-to-runtime | `omp` |
| OrcaDev / Orca ADE | portable-cli | documented-cli | `orca status --json` |
| Command Code | unsupported | unverified | — |
| xAI Grok Build | runtime-mcp | delegated-to-runtime | `grok` |
| GitHub Copilot | unsupported | unverified | — |
| MiMo Code | unsupported | unverified | — |
| Amp | unsupported | unverified | — |
| OpenClaude | unsupported | unverified | — |
| Hermes Agent | unsupported | unverified | — |
| Devin | unsupported | unverified | — |
| Goose | unsupported | unverified | — |
| Auggie | unsupported | unverified | — |
| Autohand Code | unsupported | unverified | — |
| Charm/Crush | unsupported | unverified | — |
| Cline | unsupported | unverified | — |
| Codebuff | unsupported | unverified | — |
| Continue | unsupported | unverified | — |
| Droid | unsupported | unverified | — |
| Kilocode | unsupported | unverified | — |
| Kimi | unsupported | unverified | — |
| Mistral Vibe | unsupported | unverified | — |
| Qwen Code | unsupported | unverified | — |
| Rovo Dev | unsupported | unverified | — |
| Meta Muse Code | runtime-mcp | delegated-to-runtime | `muse` |
| OpenMausBot | runtime-mcp | delegated-to-runtime | `openmausbot` |
| OpenMuse (Python) | runtime-mcp | delegated-to-runtime | `openmuse` |
| T3 Code | unsupported | unverified | — |
| CopilotKit OpenDots | unsupported | unverified | — |
| CopilotKit OpenBot | unsupported | unverified | — |
| agentes.chat | unsupported | unverified | — |
| OpenAI dots | unsupported | unverified | — |
| xAI Grok Bot | unsupported | unverified | — |
| Meta Muse app | unsupported | unverified | — |
| Cue by Manus | unsupported | unverified | — |

xAI Grok Build and the eleven rows after Rovo Dev are the harnesses of the Runtime
bot study of 2026-11-21. Each needs a Simplicio Runtime that lists its id in
`simplicio integrate list`, and none was verified against a real installation
of its product.

- The Runtime writes a file for Grok Build, Muse Code, OpenMausBot and OpenMuse:
  see [Grok Build](grok.md), [Muse Code](muse-code.md),
  [OpenMausBot](openmausbot.md) and [OpenMuse](openmuse.md).
- For the other eight the Runtime writes nothing, so they stay `unsupported`
  here. `simplicio integrations routes <id>` prints the steps of
  [OpenDots](opendots.md), [OpenBot](openbot.md), [agentes.chat](agentes-chat.md),
  [dots](dots.md), [Grok Bot](grok-bot.md), the [Muse app](muse.md) and
  [Cue](cue.md). `simplicio integrate verify --host t3-code` reports the agents
  that [T3 Code](t3-code.md) runs.
- Earlier public text described the id `grok` as another product, the
  Superagent CLI. It is xAI Grok Build.

The returned matrix contains only public contract metadata. It never includes
credentials, prompt bodies, configuration bodies, or host process output.
