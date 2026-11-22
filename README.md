<div align="center">

<img src="assets/simplicio-icon-192.png" alt="Simplicio logo" width="96" height="96">

<h1>Simplicio</h1>

<p><b>UltraFast Mode for all.</b></p>

<p><b>Same agent, same model, same job: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, and $0.0226&nbsp;→&nbsp;$0.0076.</b></p>

<p>Without Simplicio → with Simplicio 3.15.0. Median of 3 runs of one small coding job in Claude Code with Claude Haiku 5.5.</p>

<p>Simplicio runs on your machine and adds tools to the coding agent you already use.</p>

<p>
  <a href="https://github.com/simpletibr/simplicio/releases/latest"><img src="https://img.shields.io/github/v/release/simpletibr/simplicio?color=2fe6a0&label=release" alt="Latest release"></a>
  <a href="https://simpleti.com.br/simplicio/docs"><img src="https://img.shields.io/badge/docs-simpleti.com.br-ffd23f" alt="Documentation"></a>
  <a href="https://github.com/simpletibr/simplicio/stargazers"><img src="https://img.shields.io/github/stars/simpletibr/simplicio?style=social" alt="Stars"></a>
  <img src="https://img.shields.io/badge/license-Proprietary-red" alt="License: proprietary">
</p>

<p>
  English ·
  <a href="READMEs/README.pt-BR.md">Português (Brasil)</a> ·
  <a href="READMEs/README.es-ES.md">Español</a> ·
  <a href="READMEs/README.fr-FR.md">Français</a> ·
  <a href="READMEs/README.it-IT.md">Italiano</a> ·
  <a href="READMEs/README.pl-PL.md">Polski</a> ·
  <a href="READMEs/README.ru-RU.md">Русский</a> ·
  <a href="READMEs/README.zh-CN.md">简体中文</a> ·
  <a href="READMEs/README.ja-JP.md">日本語</a> ·
  <a href="READMEs/README.ko-KR.md">한국어</a> ·
  <a href="READMEs/README.hi-IN.md">हिन्दी</a> ·
  <a href="READMEs/README.ar-SA.md">العربية</a>&lrm; ·
  <a href="READMEs/README.he-IL.md">עברית</a>&lrm; ·
  <a href="READMEs/README.id-ID.md">Bahasa Indonesia</a> ·
  <a href="READMEs/README.ms-MY.md">Bahasa Melayu</a>
</p>

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-2026-11-22-dark.svg">
    <img src="assets/benchmark-2026-11-22-light.svg" width="840" alt="Bar chart comparing no Simplicio, Simplicio 3.14.0 and Simplicio 3.15.0 on three measures, median of three sessions each. Time for the whole job: 121 s with no Simplicio, 104 s with Simplicio 3.14.0 and 25 s with Simplicio 3.15.0. Cost: $0.0226, $0.0220 and $0.0076. Output tokens: 18,162, 19,722 and 3,211.">
  </picture>
</p>

<p align="center">
  <sub>Median of 3 sessions for each setup (no Simplicio, Simplicio 3.14.0 and Simplicio 3.15.0). Claude Haiku 5.5 in Claude Code 2.1.330, 2026-11-22. Every setup delivered 9 of 9 steps. The thin line on each bar runs from the lowest to the highest session.<br>
  <a href="benchmarks/2026-11-22-standard-benchmark.md">Method, data and limits</a></sub>
</p>

<p align="center">
  <sub>Read with it: one small job, three sessions per setup, one model. The outside checks are narrower than the prompts. Peak memory was higher: 375 MB against 270 MB. The Simplicio builds were compiled from the release commits, with sign-in off.</sub>
</p>

<p align="center">How Simplicio gets this result is not published. The measurements are, including the ones where it loses.</p>

<p align="center">
  <b>Try it:</b> <a href="#install">Install</a> · <a href="#first-run">First run</a><br>
  <a href="#what-simplicio-is">What it is</a> ·
  <a href="#the-measurement">Measurement</a> ·
  <a href="#works-with-the-agent-you-already-use">Agents</a> ·
  <a href="#command-line">Commands</a> ·
  <a href="#safety-and-privacy">Privacy</a> ·
  <a href="#questions-people-ask">Questions</a> ·
  <a href="#documentation-and-community">Docs</a>
</p>

## What Simplicio is

Simplicio is a local program that gives the coding agent you already use an ultra-fast mode, whatever the agent and whatever the model. The numbers on this page come from one agent and one model; the section below says exactly what was measured.

- **You keep your agent and your model.** Simplicio does not replace Claude Code, Codex, Cursor or the model behind them.
- **One signed binary** registers itself in your agents and runs on your machine as a local STDIO MCP server.
- **What changes is the session.** Its time and its cost.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/diagram-where-simplicio-runs-dark.svg">
    <img src="assets/diagram-where-simplicio-runs-light.svg" width="840" alt="Diagram. On your machine: you, your coding agent, Simplicio and your repository. The agent talks to Simplicio over local STDIO (MCP). The agent talks to your model provider as before. Simplicio talks to SimpleTI for sign-in and plan checks and to GitHub for a release check, with no repository content in either.">
  </picture>
</p>

<p align="center">
  <sub>The default flow. <a href="#safety-and-privacy">The full list</a> has the other services.</sub>
</p>

<details>
<summary>MCP and STDIO</summary>

MCP is the Model Context Protocol, the way a coding agent calls outside tools. STDIO means the agent launches the program itself and talks to it through its standard input and output.

It gives your agent tools. A repository map, bounded context, structured edits and checks. [The core tools](#works-with-the-agent-you-already-use) are listed below.

You install one signed native binary. The installer verifies the signature, then registers Simplicio in the agents it finds on your machine.

</details>

## The measurement

One job, run the same way with and without Simplicio: three steps in one agent session, each result checked from outside.

1. Build a user listing: an API and a page with a table, search and sorting.
2. Change it: drop a column, add a role filter and a date column.
3. Add a registration: a `POST` endpoint that checks its input, and a form page.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-2026-11-22-sessions-dark.svg">
    <img src="assets/benchmark-2026-11-22-sessions-light.svg" width="840" alt="Scatter plot of every session, with the time for the whole job across and the cost reported by the agent up. Simplicio 3.15.0, green diamonds: 23 to 27 s and $0.0071 to $0.0098. Simplicio 3.14.0, grey squares: 90 to 106 s and $0.0214 to $0.0249. No Simplicio, hollow circles: 97 to 172 s and $0.0186 to $0.0280.">
  </picture>
</p>

| Measure | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| Job time | 121 s<br><sub>97–172</sub> | 104 s<br><sub>90–106</sub> | **25 s**<br><sub>23–27</sub> |
| Reported cost | $0.0226<br><sub>0.0186–0.0280</sub> | $0.0220<br><sub>0.0214–0.0249</sub> | **$0.0076**<br><sub>0.0071–0.0098</sub> |
| Model requests | 25<br><sub>19–33</sub> | 18<br><sub>18–22</sub> | **10**<br><sub>10–10</sub> |
| Tool calls | 22<br><sub>16–30</sub> | 15<br><sub>15–19</sub> | **7**<br><sub>7–7</sub> |
| Output tokens | 18,162<br><sub>15,599–23,328</sub> | 19,722<br><sub>18,764–24,997</sub> | **3,211**<br><sub>3,068–3,573</sub> |
| Input tokens | 34,691<br><sub>30,447–42,543</sub> | 34,141<br><sub>33,121–40,017</sub> | 18,755<br><sub>18,466–33,300</sub> |
| CPU time | 8.5 s<br><sub>8.5–9.2</sub> | 10.0 s<br><sub>8.9–10.0</sub> | **5.3 s**<br><sub>5.3–5.5</sub> |
| Peak memory | **270 MB**<br><sub>248–274</sub> | 436 MB<br><sub>432–439</sub> | 375 MB<br><sub>365–379</sub> |
| Steps delivered | 9 of 9 | 9 of 9 | 9 of 9 |

Median of 3 sessions, lowest to highest under each value. Bold marks the best value in a row where ranges do not overlap. "9 of 9" is 3 steps in each of 3 sessions, all passing every outside check.

Requests and tool calls per session.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-2026-11-22-work-dark.svg">
    <img src="assets/benchmark-2026-11-22-work-light.svg" width="840" alt="Unit chart with one mark per model request or tool call, median of 3 sessions. Model requests: 25 with no Simplicio, 18 with Simplicio 3.14.0 and 10 with Simplicio 3.15.0. Tool calls: 22, 15 and 7.">
  </picture>
</p>

Time by step, on one shared scale.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-2026-11-22-steps-dark.svg">
    <img src="assets/benchmark-2026-11-22-steps-light.svg" width="840" alt="Median time by step on one shared scale. Step 1, build: 57.3 s with no Simplicio, 53.7 s with Simplicio 3.14.0 and 5.8 s with Simplicio 3.15.0. Step 2, change: 17.3 s, 15.2 s and 8.9 s. Step 3, register: 31.4 s, 27.5 s and 10.3 s.">
  </picture>
</p>

<details>
<summary>Exact numbers by step</summary>

Each cell is the median time and the median cost of the step:

| Step | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |
|---|---|---|---|
| 1. Build | 57.3 s / $0.0111 | 53.7 s / $0.0137 | 5.8 s / $0.0022 |
| 2. Change | 17.3 s / $0.0040 | 15.2 s / $0.0032 | 8.9 s / $0.0023 |
| 3. Register | 31.4 s / $0.0075 | 27.5 s / $0.0056 | 10.3 s / $0.0026 |

</details>

**How to read it.** The whole job ran 4.9 times faster at about a third of the cost; even the fastest session without Simplicio (97.1 s) was 3.7 times slower than the slowest with 3.15.0 (26.6 s). [Method, limits](benchmarks/2026-11-22-standard-benchmark.md#limits)

<details>
<summary>How each number is defined</summary>

- The ratios come from the unrounded medians. Against the previous release the whole job ran 4.2 times faster.
- Each median is taken separately, so the steps do not add up to the whole-job median.
- Worst case: the fastest session without Simplicio (97.1 s) was still 3.7 times slower than the slowest session with Simplicio 3.15.0 (26.6 s), and the cheapest session without it ($0.0186) still cost 1.9 times as much as the most expensive session with it ($0.0098).
- The baseline is Claude Code 2.1.330 with its own tools, no MCP server and no Simplicio configuration.
- Each step is checked from outside the session: the API is called over HTTP and the pages are loaded in headless Chrome, which is Chrome without a window.
- The checks do not test the search box, sorting, the redirect after saving, the look of the page or the quality of the code.
- A model request is one call to the model; a tool call is one use of a tool by the agent.
- Reported cost is the tokens used times the model's published price. It counts model tokens only. It is not an invoice.
- The input-token ranges overlap, so this run claims no difference in input tokens.
- Four sessions ran at a time on one machine: compare times only inside this round.

</details>

### Where Simplicio does not win

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/benchmark-2026-11-22-memory-dark.svg">
    <img src="assets/benchmark-2026-11-22-memory-light.svg" width="840" alt="Peak memory, median of 3 sessions: 270 MB with no Simplicio, the lowest; 436 MB with Simplicio 3.14.0, 61% more; 375 MB with Simplicio 3.15.0, 39% more.">
  </picture>
</p>

- **Memory.** Peak memory was 39% higher: 375 MB against 270 MB.
- **The previous release showed no gain on this job.** Simplicio 3.14.0 cost the same as no Simplicio.
- **A short one-off Python script.** Simplicio 3.10.8 was slower (19.6 s against 11.4 s) and was not measured again.
- **What you install is not exactly what was measured.** The builds were compiled from the release commits, with sign-in off.
- **The sample is small.** Three sessions per setup, one model, one project.

<details>
<summary>The limits in full</summary>

- **Memory.** Peak memory was 39% higher than with the plain agent: 375 MB against 270 MB.
- **The previous release showed no gain on this job.** Simplicio 3.14.0 cost the same as no Simplicio, and its time difference is inside the run-to-run spread. The gain arrived with 3.15.0.
- **A short one-off Python script.** In an earlier round, Simplicio 3.10.8 was slower than the plain agent with every model tried: on Claude Sonnet 5.5 in Claude Code, 19.6 s and $0.0548 against 11.4 s and $0.0283. Not measured again on 3.15.0.
- **What you install is not exactly what was measured.** The builds were compiled from the release commits, with sign-in and the background process off. The signed downloads were not measured.
- **The sample is small.** Three sessions per setup, one model, one small new project, one machine, four sessions at once; none dropped or re-run. The ratios measure this job, not yours, and we have not measured how much of your work looks like it.

</details>

### Check it yourself

[The report](benchmarks/2026-11-22-standard-benchmark.md) publishes the three prompts (in Portuguese, with a translation), every outside check and every session; [the data file](benchmarks/2026-11-22-standard-benchmark.json) has them as JSON. The test harness is not published.

## Install

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex
```

Python (PyPI):

```bash
python3 -m pip install --upgrade simplicio-installer
simplicio install
```

On Windows, use `py -m pip install --upgrade simplicio-installer` and then `simplicio install`.

The installer verifies the signed release and automatically registers Simplicio in the agents it finds. Then sign in with `simplicio auth login`.

<details>
<summary>Install details</summary>

- It downloads the latest signed release for your platform and checks its SHA-256 and its Ed25519 signature before it replaces the installed binary.
- The binary goes under `~/.simplicio/bin/` (on Windows, `%USERPROFILE%\.simplicio\bin\`), and Simplicio is automatically registered in the agents it finds. A registration failure stops the installer instead of reporting success.
- Restart any agent that is already open so it reloads its configuration. If the Python script directory is not on your `PATH`, add it first.

**Sign in.** A Google sign-in is required, including during the beta. Run `simplicio auth login`, then `simplicio auth status --json`, and continue when it reports `active: true`. Registration works before you sign in. Never paste a password or token into an agent's configuration.

To confirm Simplicio loaded, look for `simplicio` in the agent's list of MCP servers. In Claude Code, `/mcp` lists the connected servers. Prefer to read the installer first? It is [install.sh](install.sh).

To update, run either installer again at any time: it resolves the latest release. `install.sh` and `install.ps1` are in the root of this repository.

```bash
# macOS / Linux
sh install.sh --doctor
sh install.sh --uninstall --keep-data
sh install.sh --uninstall --purge       # needs SIMPLICIO_CONFIRM_PURGE=1; preserves ~/.simplicio/.env
```

```powershell
# Windows
pwsh install.ps1 -Doctor
pwsh install.ps1 -Uninstall -KeepData
pwsh install.ps1 -Uninstall -Purge      # needs SIMPLICIO_CONFIRM_PURGE=1; preserves .env
```

- `--doctor` checks the installation.
- `--uninstall --keep-data` removes the installed binary and keeps your data. That includes the 30-day Google sign-in state in `~/.simplicio/login.json`.
- `--uninstall --purge` removes only the state Simplicio manages, the sign-in state included. It keeps `~/.simplicio/.env`, where provider credentials may live. A purge needs `SIMPLICIO_CONFIRM_PURGE=1`.
- Uninstall does not edit your agents' configuration. The Simplicio entries stay in each agent until you remove them in that agent's own settings.
- Data inside a project's own `.simplicio` folder is not removed by `--keep-data`. Look at the target before you choose `--purge`.

Full details: [INSTALL.md](INSTALL.md).

</details>

## First run

```bash
simplicio version
cd my-project
simplicio onboard
```

`simplicio version` checks the install; `simplicio onboard` prepares the project. Then open your agent there.

## Works with the agent you already use

The installer hands registration to Simplicio's own registrar. It writes the Simplicio entry for the agents it knows how to configure, among them Claude Code, Codex, Cursor, Visual Studio Code, OpenCode, Gemini CLI and Kiro.

The registry [`plugins/simplicio/host-surfaces.json`](plugins/simplicio/host-surfaces.json) names 43 agent ids; the matrix [`docs/hosts/compatibility-matrix.md`](docs/hosts/compatibility-matrix.md) marks 12 supported and 29 `unverified`. Treat an `unverified` integration as untested.

<details>
<summary>All 43 agents</summary>

- The registry names 43 agent ids and how Simplicio reaches each: an MCP entry that Simplicio writes (23), a native plugin or extension (5), a portable plugin package (4), a guided setup you follow yourself (9), or another command-line tool (2).
- The matrix has no row for Codex and Gemini CLI. Even where the registry says Simplicio writes the entry, treat an `unverified` integration as untested.
- 23 agents have a guide in [`docs/hosts/`](docs/hosts/). For agents reached through a plugin, the plugin is applied in a separate step that asks for your consent, and [INSTALL.md](INSTALL.md) describes it.

| How Simplicio reaches it | Count | Agents |
|---|---|---|
| An MCP entry that Simplicio writes | 23 | **xAI Grok Build**, MiMo Code, Amp, OpenClaude, Antigravity, **Pi**, **oh-my-pi**, Goose, Auggie, Autohand Code, Charm, Cline, Command Code, Continue, Droid, Kilocode, Kimi, Mistral Vibe, Rovo Dev, **Visual Studio Code**, **Meta Muse Code**, **OpenMausBot**, **OpenMuse (Python)** |
| A native plugin or extension | 5 | **Claude Code**, Codex, **OpenCode**, Hermes Agent, Gemini CLI |
| A portable plugin package | 4 | **Cursor**, GitHub Copilot, **Kiro**, Qwen Code |
| A guided setup you follow yourself | 9 | Devin, Codebuff, CopilotKit OpenDots, CopilotKit OpenBot, agentes.chat, OpenAI dots, xAI Grok Bot, Meta Muse app, Cue by Manus |
| Another command-line tool | 2 | **OrcaDev / Orca ADE**, T3 Code |

Bold: the compatibility matrix marks the agent as supported.

</details>

These are the core tools your agent gets:

| Tool | What it gives you |
|---|---|
| `simplicio_map` | A compact map of the repository, so the agent finds its way around |
| `simplicio_context` | The context a task needs, bounded, instead of whole files |
| `simplicio_edit` | Structured file edits from a prepared plan |
| `simplicio_validate` | Pipeline, test and delivery checks |
| `simplicio_run` | A task run under Simplicio's control |

[MCP-CONNECT.md](MCP-CONNECT.md) describes the core tools.

<details>
<summary>Manual configuration</summary>

Simplicio is a local STDIO MCP server, so an agent that can start a local MCP server can be pointed at it. To repeat the registration, run `simplicio mcp register`. The server command is `simplicio serve --mcp --stdio`.

If your agent was not configured for you, add this entry to its MCP configuration. Replace the path with the absolute path of the installed binary.

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

Codex reads TOML. Agents start `command` directly, so do not use `~` and do not rely on shell expansion. Use forward slashes in Windows paths, and replace the example user name.

Windows:

```toml
[mcp_servers.simplicio]
command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"
args = ["serve", "--mcp", "--stdio"]
```

macOS:

```toml
[mcp_servers.simplicio]
command = "/Users/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Linux:

```toml
[mcp_servers.simplicio]
command = "/home/your-name/.simplicio/bin/simplicio"
args = ["serve", "--mcp", "--stdio"]
```

Where each agent keeps its file: [MCP-CONNECT.md](MCP-CONNECT.md).

</details>

## Command line

| Command | What you get |
|---|---|
| `simplicio map --repo . --for-llm markdown` | A compact structural map of the repository, written for a model to read |
| `simplicio context --repo .` | The bounded context for a task |
| `simplicio memory query "query" --json` | What the project already knows, recalled from its indexed memory, as JSON |
| `simplicio edit --plan plan.json --repo .` | A prepared set of structured edits, applied to the files |
| `simplicio run "task" --repo . --agents N` | A task run with N agents under Simplicio's control |
| `simplicio loop` | Work that goes on in rounds until it converges |

The names you will see in Simplicio's messages: Mapper observes, Fast projects or retrieves, Dev CLI edits, Runtime governs, and Loop converges.

## Safety and privacy

This section describes version 3.15.0.

- **Stays on your machine.** Mapping, context, edits and checks run inside the Simplicio binary.
- **To SimpleTI (simpleti.com.br).** Sign-in and plan checks only, no repository content.
- **To GitHub.** A release check you can turn off.
- **No analytics.** Simplicio uploads no analytics, crash reports or usage data.
- **To services you configure.** They receive what that feature sends, which can include prompts and code.
- **Two features reach a public service without any configuration.** Web search (DuckDuckGo) and the dependency audit (osv.dev); neither sends file contents.
- **Downloads.** From GitHub; some helper scripts also fetch tools from PyPI or npm.

<details>
<summary>The details</summary>

- **Stays on your machine.** Mapping, context, edits and checks run inside the Simplicio binary. It hands the results to your agent on the same machine. Usage and savings records are local files. What your agent sends to its own model provider is decided by the agent, as before.
- **To SimpleTI (simpleti.com.br).** Sign-in and plan checks only, with no repository content: no files, file paths, prompts or edits.
  - They carry your sign-in token, the Simplicio version and your computer's host name. An optional license lookup also carries your account e-mail.
  - They return your account e-mail, name and plan.
- **To GitHub.** A background check for a new release, at most about once every 12 hours, carrying nothing about you or your code. Set `SIMPLICIO_DISABLE_AUTO_UPDATE=1` to turn it off. An update downloads the binary from GitHub and checks its SHA-256 and signature before it replaces the old one.
- **No analytics.** Simplicio 3.15.0 and the files it installs into your agents were checked for this: none uploads analytics, crash reports or usage data. The hooks it installs run local programs only (the Simplicio binary and, for optional plugins, local scripts); none of them contacts the network.
- **To services you configure.** A model provider, GitHub, Jira, a chat notifier or a team cache receive what that feature sends, which can include prompts and code. Requests to a model provider carry a header that names Simplicio as the client.
- **Two features reach a public service without any configuration.** Neither sends file contents.
  - Web search, when it runs, sends the search query to DuckDuckGo unless you configure another search service. In Simplicio's own chat, a message that looks like a web question can become that query.
  - The dependency security audit, when you run it, sends the names and versions of your dependencies to osv.dev.
- **Downloads.** The installer and the update path download from GitHub. Some optional helper scripts fetch their own tools from PyPI or npm when you run them. An agent plugin that finds no Simplicio binary downloads the official installer from GitHub, pinned to a commit and checked by SHA-256.

**Signed releases.** Each release publishes its binaries with SHA-256 checksums, Ed25519 signatures, an SBOM (a list of what is in the build) and build provenance.

The installers and the update path check the checksum and the signature before they replace the installed binary. For stable releases a missing or invalid signature and a checksum mismatch are hard failures; the contract is in [docs/UPDATE_SIGNATURE_CONTRACT.md](docs/UPDATE_SIGNATURE_CONTRACT.md).

**What the installer changes in your agent.**

- It adds a Simplicio entry to the agent's MCP configuration and keeps the rest of the configuration.
- In Claude Code it also allows `mcp__simplicio__*`, so a Simplicio tool is not denied in auto mode.
- In agents whose hook interface the installer has verified, it also installs Simplicio's hooks there.
- Uninstall does not undo these entries; the Install section says how to remove them. [INSTALL.md](INSTALL.md) says what the installer writes, and the guide of each agent in [`docs/hosts/`](docs/hosts/) gives the detail.

</details>

## Also in this repository

<details>
<summary>Desktop app (macOS preview)</summary>

A macOS (Apple Silicon) Desktop preview is published as [Simplicio-3.8.47-arm64.dmg](https://github.com/simpletibr/simplicio/releases/download/v3.8.47/Simplicio-3.8.47-arm64.dmg). Its SHA-256 is in [DESKTOP-SHA256SUMS](DESKTOP-SHA256SUMS), separate from the checksums of the Simplicio binaries. The DMG has no signature file and bundles the Simplicio 3.8.47 binary.

- Windows Desktop is not published. On Windows, use the command-line install above.
- Apple Developer ID signing and notarization are not done. The package is ad-hoc signed, which means without an Apple developer certificate, and Gatekeeper acceptance is not claimed, so macOS may warn you when you open it.
- The command-line install above is the supported public installation path until a signed Desktop package is published.

Details: [docs/desktop/RELEASE.md](docs/desktop/RELEASE.md).

</details>

<details>
<summary>For maintainers: the generated flow diagram</summary>

- The commands and tools documented in README.md and MCP-CONNECT.md are drawn as one flow, [docs/flow/simplicio.svg](docs/flow/simplicio.svg), generated from one source file, `docs/flow/simplicio.flow.json`.
- Regenerate it with `python3 scripts/generate_flow.py` and check it for drift with `python3 scripts/generate_flow.py --check`.
- The contract that keeps it in step with this page and with MCP-CONNECT.md is `python3 -m pytest tests/test_flow_contract.py -q`.
- The Langflow import check is `scripts/verify_flow_langflow.py`, which fails closed (exit 2, `status=blocked`) when no server is running. The evidence is under `docs/flow/evidence/` and `docs/flow/render/`; [docs/flow/README.md](docs/flow/README.md) has the requirements and how to repeat it.

</details>

## Questions people ask

**Is the comparison fair?**<br>
Same agent, model, prompts, project and outside checks; the baseline has no Simplicio. See [where it does not win](#where-simplicio-does-not-win).

**Do I have to change my agent or my model?**<br>
No. Simplicio plugs into the agent you already use.

**Will I always get these numbers?**<br>
No. They measure one job, one model and one machine.

**Is it open source?**<br>
No. Simplicio is proprietary: a signed binary. This repository holds the installers, packages, docs and data.

**How do I remove it?**<br>
Run `sh install.sh --uninstall --keep-data`, or `pwsh install.ps1 -Uninstall -KeepData` on Windows. It does not edit your agents' configuration, so remove the Simplicio entries in each agent's own settings.

**Do I need an account?**<br>
Yes. A Google sign-in is required, including during the beta. Run `simplicio auth login`.

**Does my code leave my machine?**<br>
Mapping, context, edits and checks run on your machine; SimpleTI and GitHub get no repository content. [Details](#safety-and-privacy).

## Documentation and community

- **Website:** [simpleti.com.br/simplicio](https://simpleti.com.br/simplicio/)
- **Documentation:** [simpleti.com.br/simplicio/docs](https://simpleti.com.br/simplicio/docs)
- **Discord:** [Join the community](https://discord.gg/wM6tr7xVb)
- **Issues:** [GitHub issue tracker](https://github.com/simpletibr/simplicio/issues)
- **Related:** Simplicio Video (hypit): `git clone https://github.com/hypit-ai/hypit.git simplicio-video`

<p align="center">
  <sub>© 2026 SimpleTI. Simplicio is a registered proprietary software. All rights reserved.</sub>
</p>
