# Desktop documentation

Contracts, designs and procedures for Simplicio Desktop. The product source lives under `apps/desktop/`; this folder holds the written contracts. Dated session records are kept in [`archive/`](archive/).

| File | Use |
| --- | --- |
| [`ACTIVITY-CENTER.md`](ACTIVITY-CENTER.md) | Spec for activity.center/v1, the read-only history of bounded receipts; filters and exports use a projection, and raw ledgers stay out of the Desktop |
| [`ACTIVITY-REPLAY.md`](ACTIVITY-REPLAY.md) | Spec for Desktop activity replay: bounded daemon polling, deterministic run projection, redacted AI-BOM export, and the one-second poll latency budget |
| [`ADR-0001-public-tauri-shell.md`](ADR-0001-public-tauri-shell.md) | Decision record for a Tauri 2 public Desktop shell that supervises a separate signed Runtime sidecar, with the Runtime owning identity, entitlements, providers and receipts |
| [`AMBIENT-CONTROLS.md`](AMBIENT-CONTROLS.md) | Spec for ambient.controls/v1: Off, Suggestions Only, Ask Before Acting and Autonomous Within Policy, defaulting to Suggestions Only with state persisted in the Runtime |
| [`AMBIENT-OS.md`](AMBIENT-OS.md) | Spec for the ambient OS projection: a read-only ambient.state/v1 signal of quiet, working, attention or unavailable that never starts work or runs a local loop |
| [`AUTH.md`](AUTH.md) | Desktop login contract: a Runtime-owned device authorization flow in the system browser, authentication-only capability negotiation, account-state recovery, and logout limits |
| [`AUTOMATION-STUDIO.md`](AUTOMATION-STUDIO.md) | Spec for automation.studio/v1 suggestions and drafts: each suggestion starts in review_required and cites its receipt, with Accept and Save draft disabled for unverified sources |
| [`BOT-CENTER-STATUS.md`](BOT-CENTER-STATUS.md) | Status of the Bot Center projection: bounded and fail-closed, with desktop_bot_action returning agent_api_unavailable until the Runtime Bot, delivery, Room and Computer contracts exist |
| [`BOT-MODE.md`](BOT-MODE.md) | Boundary for the Desktop Bot Center as a projection client over the bounded bot-center-snapshot/v1, which owns no agent loop, approval gate or Bot registry |
| [`BRIEFINGS.md`](BRIEFINGS.md) | Spec for ambient.briefing/v1, a receipt-backed summary of at most three items whose schedule and delivery stay unconfigured until the user opts in through Runtime |
| [`CAPABILITY-CENTER.md`](CAPABILITY-CENTER.md) | Spec for capability.registry/v1, the single discovery surface for Desktop Apps and the + New launcher, actionable only after a healthy Runtime probe |
| [`CAPABILITY-WIDGETS.md`](CAPABILITY-WIDGETS.md) | Spec for capability.widgets/v1: optional read-only Today widgets, at most three per user, empty by default, configured through the Runtime and linked back to canonical views |
| [`CHAT-CONTRACT.md`](CHAT-CONTRACT.md) | Contract for chat.session/v1, a Desktop projection of the Runtime Session Service whose composer is enabled only when the Agent API is authoritative |
| [`DESIGN.md`](DESIGN.md) | Desktop design system and accessibility baseline: light-native tokens in src/styles.css, pt-BR default locale, named motion durations, and guided installer and workbench rules |
| [`DESKTOP-EPIC.md`](DESKTOP-EPIC.md) | Desktop epic architecture: a Tauri and React projection client with an authority split in which the Runtime owns sessions, approvals, receipts and Computer leases |
| [`FLAGSHIP-APPS.md`](FLAGSHIP-APPS.md) | Lists six flagship Desktop Apps (Video, Browser, Computer, Research, Files/PDF, Code/Build) built on capability.request/v1 with shared Chat, Work Item and artifact identities |
| [`FLEET-ORIENTATION.md`](FLEET-ORIENTATION.md) | Measures first worktree orientation from the Runtime's shared default-branch map baseline, with timings, reproduction commands and load-related outliers |
| [`IMPLEMENTATION.md`](IMPLEMENTATION.md) | Desktop v1 implementation contract: a Tauri shell over the signed Runtime sidecar, four access states, a bounded redacted snapshot and governed, non-executed mutations |
| [`INSTALLED-E2E.md`](INSTALLED-E2E.md) | Acceptance procedure for the installed Desktop: native checks, the #375 report schema and its twelve gates, plus what preview or mocked-IPC tests cannot prove |
| [`LAUNCHER.md`](LAUNCHER.md) | Spec for desktop.launcher/v1, the + New menu with stable capability IDs for five actions, disabled until a Runtime probe verifies them |
| [`LIBRARY.md`](LIBRARY.md) | Spec for library.artifacts/v1: a view over the Runtime artifact graph of handles, versions and provenance, not a hidden local copy or second file store |
| [`LIVE-MISSION-CONTROL.md`](LIVE-MISSION-CONTROL.md) | Spec for live.mission-control/v1, a contextual projection of active Work Items that appears only while work runs, waits, pauses or blocks |
| [`MACOS-ARM64-ACCEPTANCE-GATE.md`](MACOS-ARM64-ACCEPTANCE-GATE.md) | Gate for closing issue #375: what this Linux workspace cannot prove for macOS arm64, and what a Mac owner must attach as a redacted installed-acceptance report |
| [`MOTION.md`](MOTION.md) | Motion policy: named semantic durations, never delaying a click, approval or navigation, and createMotionPolicy(true) removing decorative motion while keeping state changes visible |
| [`MULTI-CHAT.md`](MULTI-CHAT.md) | Spec for chat.workspace/v1, a bounded session index linking each chat to a canonical session_id, Bot ID and Runtime revision, with controls disabled until Session Service authority is verified |
| [`OMNISEARCH.md`](OMNISEARCH.md) | Spec for search.omni/v1: a keyboard-first index of capabilities, Chats, Teams, Work Items and Library artifacts that stores labels and safe handles, not secrets |
| [`OPTIONAL-CAPABILITIES.md`](OPTIONAL-CAPABILITIES.md) | Spec for optional.capabilities/v1: Voice, Computer, Learning Journey and Insights with independent reason codes, never claiming a backend exists while unavailable |
| [`PRODUCT-STATES.md`](PRODUCT-STATES.md) | Desktop product state machine and screen inventory: signed-out, checking, active, inactive and unknown states, plus a visual direction that later files supersede |
| [`PROVIDER-ACCOUNTS-IMPLEMENTATION.md`](PROVIDER-ACCOUNTS-IMPLEMENTATION.md) | Implementation boundary for Desktop provider account management: Add Account stays disabled until a Runtime-owned account store and isolated authentication exist |
| [`PROVIDER-CONTRACT.md`](PROVIDER-CONTRACT.md) | Desktop provider contract: host status semantics (connected, detected, needs_attention, not_installed), the initial host matrix, and the v2 provider quota telemetry boundary |
| [`PROVIDERS.md`](PROVIDERS.md) | Desktop provider registry: canonical connected, registered, detected, needs_attention and not_installed states, and the reviewed MCP integration install flow with digest-checked consent |
| [`REFERENCE-COVERAGE.md`](REFERENCE-COVERAGE.md) | Desktop screen-coverage map: which screens, routes and token-report flows exist, what is hidden, and what each one is limited to |
| [`RELEASE-3.8.41-PREFLIGHT.md`](RELEASE-3.8.41-PREFLIGHT.md) | Blocked local preflight record for Desktop 3.8.41 on Apple Silicon: evidence only, no public release, issues 282 and 283 stay open |
| [`RELEASE-CONTRACT.md`](RELEASE-CONTRACT.md) | Short projection of the desktop.release/v1 model: channels, the signed-update rule behind the Check for Updates dialog, and the rule against trusting version strings |
| [`RELEASE.md`](RELEASE.md) | Normative Desktop release and updater contract: manual delivery, public v3.8.47 gate status, updater transaction, bundle identity and the authentication-only release probe |
| [`REMOTE-FLEET.md`](REMOTE-FLEET.md) | Desktop view of remote Simplicio runtimes: config allowlist, read-only health probe, mobile layout and one pause or resume worker steering action |
| [`REVIEW.md`](REVIEW.md) | Desktop review flow contract: diff digest, auto-merge eligibility, inbox handoff to the agent, and guarded commit and push with receipts |
| [`SCRIPTED-API.md`](SCRIPTED-API.md) | Desktop-side contract of the local authenticated scripted API: discovery file, bearer token, selectors, routes, error codes and the commit, push and wait semantics |
| [`SETTINGS-CONTRACT.md`](SETTINGS-CONTRACT.md) | Short contract for the settings projection: grouped providers, models, tools and skills, with authentication and secrets write-only |
| [`SIDECAR.md`](SIDECAR.md) | Desktop supervision of one Runtime sidecar: four states, bounded exponential restart backoff, a circuit after three failures, and no uncontrolled second process |
| [`SUGGESTION-INBOX.md`](SUGGESTION-INBOX.md) | Short contract for suggestions derived from receipts: each stays review-required until a person acts, and previews cannot create automations |
| [`TEACH-RECORDER.md`](TEACH-RECORDER.md) | Contract for the teach recorder: records only explicit steps after visible consent, redacts secrets, and reviews a dry run before any draft is saved |
| [`TEAM-ROOMS.md`](TEAM-ROOMS.md) | Contract for Team Rooms: one canonical identity with Discuss, Execute and Review modes; mode changes stay disabled until the Runtime contract is verified |
| [`TOKEN-REPORTS.md`](TOKEN-REPORTS.md) | Token report contract: Runtime SQLite-backed usage per project and window, consolidated multi-project view, and exports that never invent zeros or savings |
| [`TRAY-NOTIFICATIONS.md`](TRAY-NOTIFICATIONS.md) | Contract for tray and native notifications: shown for attention or active work only, bounded summaries, no prompts or credentials, and no keep-alive while idle |
| [`WORK-ITEMS.md`](WORK-ITEMS.md) | Work Item projection contract: shared identity linking task, room, bot, session and approval; the Desktop shows Runtime progress and only Runtime-permitted actions |
| [`WORKSPACE-CONTRACT.md`](WORKSPACE-CONTRACT.md) | Projection contract for Workspace identity: Spaces, Teams, Rooms and shared-memory scopes, with membership and writes disabled until the Runtime verifies them |
| [`WORKSPACE-E2E.md`](WORKSPACE-E2E.md) | Conformance E2E plan for the Workspace OS: packaged Desktop against a real installed Runtime fixture; missing setup is failure, never mocked away |
| [`WORKSPACE-EPIC.md`](WORKSPACE-EPIC.md) | Workspace OS program plan: one Desktop experience, five primary destinations, Runtime as sole authority, and remaining acceptance tied to Runtime contracts |
| [`WORKSPACE-RESOURCES.md`](WORKSPACE-RESOURCES.md) | Contract for workspace resources: projects, worktrees, files and profiles appear as safe handles, and writes go only through Runtime action descriptors |

## Archive (dated records)

| File | Use |
| --- | --- |
| [`LOCAL-ACCEPTANCE-2026-09-05.md`](archive/LOCAL-ACCEPTANCE-2026-09-05.md) | Local Desktop acceptance report of 2026-09-05: updater, telemetry and export changes, test totals, three failing generic validation tests, and what was not established |
| [`LOGIN-INSTALL-VALIDATION.md`](archive/LOGIN-INSTALL-VALIDATION.md) | Desktop login and installation audit of 2026-08-31 on Runtime 3.8.39: corrections, what the Desktop installs, remaining acceptance blockers, and local test results |
| [`MASTER-TASKS-2026-09-05.md`](archive/MASTER-TASKS-2026-09-05.md) | Desktop master task list of 2026-09-05: verified items, open end-to-end acceptance for signed install, OAuth, updates and provider sessions, and a request index |
| [`NATIVE-OBSERVATIONS-2026-09-05.md`](archive/NATIVE-OBSERVATIONS-2026-09-05.md) | Chronological native macOS audit log of the Desktop from 2026-09-05 to 2026-09-06: onboarding, login, quotas, permissions, updates, MCP status and evidence paths |
| [`QA-2026-08-31.md`](archive/QA-2026-08-31.md) | Desktop reference-implementation QA of 2026-08-31: automated test totals, native macOS validation-bundle boundaries, and what remains unverified |
| [`WORKBENCH-QA-2026-08-30.md`](archive/WORKBENCH-QA-2026-08-30.md) | Work log of the 2026-08-30 workbench, guided-setup and native QA, with the 2026-08-31 follow-up; incomplete native acceptance, not a release receipt |
