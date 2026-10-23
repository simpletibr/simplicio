# Activity replay, flight recorder and AI-BOM

Status: implemented by #432 (Part of #432). Source of truth for the TS
projection is `apps/desktop/src/activity_replay.ts`; the native bridge is
`desktop_activity_events` in `apps/desktop/src-tauri/src/lib.rs` with validation
in `activity_events.rs`.

## Event source

The Desktop reads one bounded page per poll from the resident daemon:

```
simplicio daemon events --json --cursor <n> --limit 256 --wait-ms <n>
```

- Runtime page schema: `simplicio.desktop-events-page/v1`.
- Runtime envelope schema: `simplicio.desktop-events/v1`
  (`{ schema, event, cursor, payload }`), verified against
  `schemas/desktop-events-v1.schema.json` in `simplicio-runtime`.
  `simplicio.desktop-event/v1` is accepted only as a legacy alias of the
  envelope id.
- Kinds: `run.started`, `run.progress`, `run.finished`, `plugin.installed`,
  `plugin.updated`, `plugin.removed`, `host.connected`, `host.disconnected`,
  `map.baseline.building`, `map.baseline.ready`, `update.available`,
  `update.applied`.
- `run.finished` is the only kind with a status and an optional `receipt_id`.
  Every other step reports `unknown`; the replay never infers success from
  ordering.

The native command is read-only and requires a fresh access check, like the
other Runtime read commands. Its hard bounds:

| Bound | Value |
| --- | --- |
| Events per page | 500 (the daemon serves at most 256) |
| Page bytes | 1 MB |
| Cursor | `0..9_007_199_254_740_991` (safe integer) |
| Long-poll wait | 900 ms default, 1 s maximum; the UI leaves a 250 ms gap between polls |

When the daemon is unavailable, on Windows without a daemon socket, or when the
page fails validation, the command returns an error code. The UI shows
`Eventos indisponíveis (…). Nenhum evento é inventado.` and keeps the last
valid page. Nothing is synthesized from the snapshot or from the receipt list.
The long-poll returns as soon as an event exists, so a new event reaches the
screen within the 1 s acceptance budget.

## Replay projection (`simplicio.activity-replay/v1`)

`createReplay(page)` is deterministic:

1. Events are ordered by `cursor` ascending.
2. Duplicate cursors collapse. If two different payloads claim one cursor, the
   lexicographically smallest canonical JSON form wins, so arrival order cannot
   change the result.
3. Steps are grouped by `payload.run_id`; events without a `run_id` go to the
   explicit `runtime` bucket. No event is attached to a run it did not name.
4. `worktree` is the bounded `payload.issue` of the run, when the Runtime
   reported one.
5. A run is `finished` only after a `run.finished` event, `running` only after
   `run.started`, and `unknown` otherwise.
6. Receipts are collected from `run.finished.receipt_id` only.

The projection exposes `eventCount`, `rejectedEvents`, `headCursor`,
`redactions`, `runs` and `receipts`. A malformed individual event is counted in
`rejectedEvents` and omitted; a malformed page is rejected whole.

## AI-BOM export (`simplicio.desktop-ai-bom/v1`)

`buildAiBom(replay, { source, generatedAt })` produces the JSON document, and
`aiBomToJson` / `aiBomToMarkdown` produce the two downloads. Provenance records:

- producer (`simplicio-desktop`), source (`runtime` / `preview`);
- event schema, stream id, first/last cursor, event count, rejected count;
- step and receipt counts, and the replay generation time;
- redaction policy (`simplicio.redaction/v1`): prompts, credentials and paths
  are redacted, undocumented payload fields are dropped, and the number of
  applied redactions is counted.

Redaction runs at projection time, so the same redacted text reaches both the
UI and the export. Patterns cover API-key-shaped tokens, GitHub/Slack/Bearer
tokens, `token=`/`secret=`/`password=` assignments, e-mail addresses and
personal home/`Users` paths. Unknown fields are never exported and absent
fields are rendered as `unknown`.

## UI

`ActivityScreen` keeps the receipt list and adds a `data-testid="activity-replay"`
section with:

- run selection (`<select aria-label="Selecionar execução">`);
- ordered step list with cursor, kind, status, detail and receipt;
- step-by-step playback (previous/next) over the recorded steps;
- `AI-BOM (JSON)` and `AI-BOM (Markdown)` downloads.

Static rendering and tests pass a parsed `initialEvents` page; live runs pass
`loadEvents` from `bridge.loadDesktopActivityEvents`, which polls and merges
pages with `mergeEventPages`.

## Validation

```
cd apps/desktop
npx vitest run src/activity_replay.test.ts src/activity_screen.test.ts src/screens/ActivityScreen.replay.test.tsx
npm run build
cd src-tauri && cargo check --all-targets
```

The daemon page total is also bounded in Rust (`activity_events::validate_page`),
so a direct IPC caller cannot bypass the TS limits.
