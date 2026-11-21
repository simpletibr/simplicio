# Documentation

Public documentation of this repository. Start with [`../README.md`](../README.md) and [`../INSTALL.md`](../INSTALL.md); the localized READMEs are in [`../READMEs/`](../READMEs/).

## Documents

| File | Use |
| --- | --- |
| [`2026-10-26-jev-audit.md`](2026-10-26-jev-audit.md) | Consultation of the JEV model on product levers; keeps the 28 KB context packet and flags codegen-mandatory as a disagreement |
| [`AGENT_HOST_CONTRACT.md`](AGENT_HOST_CONTRACT.md) | Mandatory map-first contract for agents and host adapters: verified project map before planning, reads, edits or provider calls |
| [`BOOTSTRAP_PROFILES.md`](BOOTSTRAP_PROFILES.md) | Two installation channels, recommended-desktop and recommended-cli, with the rules that every channel verifies before execution |
| [`FAST-PATH.md`](FAST-PATH.md) | Entry flow for any task: shape, orient, narrow, create, edit, verify, with measured costs and hard rules on when not to use a tool |
| [`FLOW.md`](FLOW.md) | Nine-step delivery flow from shape to publish: which command per step, measured cost, and optional layers to skip |
| [`HOST_INTEGRATIONS.md`](HOST_INTEGRATIONS.md) | Registry of how public installers register Simplicio with MCP hosts through the Runtime, including receipts, opt-out variables and the limits of verification |
| [`INSTALLER_HOSTS.md`](INSTALLER_HOSTS.md) | Per-host MCP configuration paths and upstream contracts for the public installers, the manual verification steps, and the two hosts that still need manual setup |
| [`INSTALL_ERROR_REGISTRY.md`](INSTALL_ERROR_REGISTRY.md) | Versioned registry of installer incidents, each fixed, guarded or open and tied to a regression test, last audited at Runtime v3.8.30 |
| [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md) | Maintainer runbook for the public Runtime and Desktop release: required assets, signature payload, local publication order, and post-release smoke gates |
| [`REPOSITORY_POLICY.md`](REPOSITORY_POLICY.md) | Policy listing what the public repository must not store, and stating that the local policy script rather than GitHub Actions is the compliance evidence |
| [`UPDATE_SIGNATURE_CONTRACT.md`](UPDATE_SIGNATURE_CONTRACT.md) | Trust contract shared by the Runtime and bootstrap installers: Ed25519 over a domain-separated digest payload, required verification order, and the pinned stable key |
| [`asolaria-integration.md`](asolaria-integration.md) | Draft architecture and roadmap for Host-8 packaging, Ed25519 signing, manifest v2 and scoreboards, self-declared subordinate to the current install documents |
| [`e2e-integration.md`](e2e-integration.md) | Guide to the seven-scenario ecosystem E2E script that runs the committed binary in a temp repo, plus the 2026-07-14 Windows transcript |
| [`testing-strategy.md`](testing-strategy.md) | Testing strategy: which suites cover source, fixtures, packages, installed apps and real hosts; coverage floors; passing tests are not release evidence |
| [`hosts/`](hosts/) | Per-host integration notes and the host compatibility matrix |
| [`flow/`](flow/) | Flow artifacts generated from one JSON source |
| [`evidence/`](evidence/) | Pointers to evidence reports |
| [`desktop/`](desktop/) | Desktop contracts, designs and procedures; see its README |

### `hosts/`

| File | Use |
| --- | --- |
| [`antigravity.md`](hosts/antigravity.md) | Google Antigravity host configuration: MCP entry running the Runtime in full profile, plus hooks that enforce simplicio tools and record savings |
| [`claude-code.md`](hosts/claude-code.md) | Claude Code host integration: exact executable detection, one managed MCP entry with full profile, pre-approved tool permissions, and receipts that are not live handshakes |
| [`codex.md`](hosts/codex.md) | Codex host integration: install the public plugin from its marketplace, bootstrap the managed Runtime, and expose the full stdio MCP surface |
| [`command-code.md`](hosts/command-code.md) | Status note: Command Code is tracked for compatibility, but automatic integration stays disabled until its executable, config scope and plugin contract are confirmed |
| [`compatibility-matrix.md`](hosts/compatibility-matrix.md) | Host compatibility matrix: capability, contract and exact probe per host, with most hosts marked unsupported and no automatic configuration writer |
| [`cursor.md`](hosts/cursor.md) | Cursor host integration: exact cursor executable detection, independent user and workspace MCP scopes, and an optional Agent Plugins v1 package |
| [`deepseek-harness.md`](hosts/deepseek-harness.md) | Status note: DeepSeek Harness stays fail-closed, with no probe and no configuration writes until an upstream contract and live evidence exist |
| [`kiro.md`](hosts/kiro.md) | Kiro host integration: exact kiro-cli detection, user or workspace MCP settings, and an atomic, idempotent write of only the managed entry |
| [`opencode.md`](hosts/opencode.md) | OpenCode native-plugin integration: a managed plugin whose execute hook rejects native file and shell tools, gated by a read-only verify command |
| [`orca.md`](hosts/orca.md) | Orca host note: exact orca executable, evidence-only verification with orca status --json, and no configuration, skill or worktree writes |
| [`pi.md`](hosts/pi.md) | Pi and oh-my-pi host integrations: separate exact probes pi and omp, separate user MCP files, atomic idempotent writes and opt-out variables |
| [`vscode.md`](hosts/vscode.md) | Visual Studio Code host integration: exact code or code-insiders detection, three explicit MCP scopes with no silent fallback, and post-write verification |

### `flow/`, `evidence/`

| File | Use |
| --- | --- |
| [`evidence/Simplicio_MCP_Token_Reuse_Evidence_Report_PT_EN.md`](evidence/Simplicio_MCP_Token_Reuse_Evidence_Report_PT_EN.md) | Pointer page for the bilingual MCP token-reuse evidence report, with its SHA-256, separating cache reuse from financial savings |
| [`flow/README.md`](flow/README.md) | Flow artifact guide: one JSON source generates the Mermaid, SVG and Langflow outputs, with drift, coverage and Langflow import gates |
