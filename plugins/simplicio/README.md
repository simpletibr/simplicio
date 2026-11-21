# Simplicio agent plugin

![Simplicio Runtime](./assets/simplicio-hero.png)

This multi-host package preserves the native Codex plugin and adds official
portable Agent Plugins v1, Claude Code, and Gemini CLI manifests. Every package
uses the verified Simplicio Runtime bootstrap, exposes its live MCP surface,
and ships the same governed Simplicio skills. The Claude Code launcher selects
the `full` MCP profile, the default for every host, in its own process only; the
portable, Codex and Gemini launchers retain their host-selected Runtime mode.

## Host packages

| Host family | Entry point | Contract |
|---|---|---|
| Codex | `.codex-plugin/plugin.json` | Native Codex plugin |
| Claude Code | `.claude-plugin/plugin.json` | Native Claude Code plugin |
| Cursor, GitHub Copilot, Kiro, Qwen Code | `plugin.json` + `mcp.json` | Agent Plugins v1 |
| Gemini CLI | `gemini-extension.json` | Native Gemini extension |
| Hermes Agent | `../simplicio-hermes/plugin.yaml` | Native Hermes Python plugin |
| Other CLI/IDE/agent harnesses | Runtime `mcp register` | MCP/config or guided integration |

The package does not pretend every product has the same plugin API. The
machine-readable `host-surfaces.json` records the surface of each of the 43 host
ids it lists. Eleven of them come from the Runtime bot study (`muse-code`,
`openmausbot`, `openmuse`, `t3-code`, `opendots`, `openbot`, `agentes-chat`,
`dots`, `grok-bot`, `muse` and `cue`), and the study also corrects `grok`. Each
of the twelve needs a Simplicio Runtime that lists its id in
`simplicio integrate list`, and none was verified against a real installation
of its product (see `docs/hosts/`). Claude Code owns its native map hooks: each
supported lifecycle event confirms or refreshes the current project map and
reuses `.simplicio/hook-context/` for the same project generation. The Runtime
still owns MCP bootstrap and authentication. Runtime mapping is preferred; if
it fails, the hook uses the bundled Mapper fallback already maintained inside
the Simplicio-managed `.simplicio` state, then stores the resulting map in the
same cache and receipt format. Both paths are map-only, and the hook never
starts Fast or another context pipeline. Hooks do not download or install
packages during a lifecycle event. If both Mapper paths fail, the host request
is denied instead of continuing without a verified map.

## Automatic Runtime bootstrap

The bundled MCP server performs an idempotent bootstrap when a supported host
first activates the package:

1. Reuse a valid Simplicio Runtime meeting `POLICY.minimumRuntimeVersion` in `bin/simplicio-mcp-bootstrap.js` when one is already present.
2. Otherwise download the official installer from an immutable repository
   commit and verify the installer SHA-256 before execution.
3. Install the pinned Runtime release through its fail-closed SHA-256 and
   Ed25519 release checks.
4. Start `simplicio serve --mcp --stdio --no-facade-mode` with stdout reserved
   exclusively for MCP JSON-RPC. Claude Code uses the adjacent
   `simplicio-claude-mcp-bootstrap.js`, which sets
   `SIMPLICIO_RUNTIME_MODE` and `SIMPLICIO_MCP_PROFILE` to `full` in that process
   only; the shared launcher is unchanged for other hosts.

The managed binary is installed at `~/.simplicio/bin/simplicio`. Existing valid
installs at `~/.local/bin/simplicio` are reused. Concurrent starts share an
installation lock, and diagnostics go to
`~/.simplicio/logs/codex-plugin-bootstrap.log`.

The Runtime supports macOS arm64/x64, Linux x64, and Windows x64. The plugin
launcher requires Node.js 18 or newer to be available to Codex MCP processes.
The official Unix installer additionally requires Python 3 and either curl or
wget. The current package is live-tested on macOS arm64; the other targets use
the same official installers but still require platform-matrix verification.

## Authentication

Installation never starts an account flow or consumes MCP stdin. Tool schemas
can load before login, while protected calls fail closed until the user
explicitly authenticates:

```bash
$HOME/.simplicio/bin/simplicio login google --json
$HOME/.simplicio/bin/simplicio auth status --json
```

## Commands and tools

The plugin does not hard-code a stale command list. The Runtime advertises its policy-governed MCP surface dynamically, so plugin
validation checks required capabilities by name instead of freezing a tool
count. `simplicio_exec` is the governed supertool for every valid
Simplicio CLI subcommand; individual CLI commands are not duplicated as separate plugin definitions.

Semantic ownership is fixed: Mapper observes (`simplicio map` /
`simplicio_map`), Fast projects or retrieves (`simplicio context` /
`simplicio_context`), Dev CLI edits (`simplicio edit`), Runtime governs, and
Loop converges (`simplicio run`). The Claude bootstrap advertises the same
`full` catalogue as every other host, including edit, run and exec;
`SIMPLICIO_MCP_PROFILE=exec` is the six-tool alternative.

Included skills:

- `simplicio-runtime`: map, recall, edit, execute, and validate through live MCP
  schemas, with the Runtime capability and interface contracts bundled locally.
- `simplicio-setup`: verify bootstrap, authentication, repair, and explicit
  global host registration.
- `simplicio-mapper`: survey repositories and produce bounded, revision-aware
  context before implementation. Claude's hooks require this layer.
- `simplicio-fast`: optional explicit project consultation over a compatible
  Mapper snapshot; it is not wired into Claude lifecycle hooks.
- `simplicio-dev-cli`: perform deterministic edits, tests, diagnostics, and
  evidence-backed validation through the Dev CLI contract.
- `simplicio-loop`: orchestrate multi-step work with bounded stages, retries,
  fan-out, recovery, and convergence.
- `simplicio-prism`: route mixed work across Mapper, Fast, Dev CLI, Loop, and
  Runtime using the bundled capability inventory and recipes.
- `simplicio-cli`: optional local tooling for the Simplicio six-layer
  task-to-code verification workflow.

The five component skills include their upstream `references/`, `agents/`,
`assets/`, and Prism helper files so Codex can use the same system contracts
without importing Runtime source code. The plugin intentionally bundles only
Simplicio first-party system skills, not the Runtime's unrelated external skill
catalog.

Source and official artwork:
<https://github.com/simpletibr/simplicio> and the Simplicio Runtime source
repository.

The host-side plugin material is MIT-licensed. The separately distributed
Simplicio Runtime and release artifacts retain their repository license.
