# Remote fleet

The Desktop can show Simplicio runtimes that live on other machines. This is a
read-mostly view: it proves which machines answer, with which version and how
fast, and refuses to enable control unless the remote is online and accepted
the configured token. No remote command is sent by this version.

## Configuration

`%USERPROFILE%\.simplicio\desktop-remotes.json` on Windows,
`~/.simplicio/desktop-remotes.json` elsewhere:

```json
{
  "schema": "simplicio.desktop-remotes/v1",
  "remotes": [
    {
      "id": "mac-mini",
      "label": "Mac mini",
      "url": "http://127.0.0.1:8787"
    },
    {
      "id": "studio",
      "label": "Studio",
      "url": "https://studio.example.test",
      "token_env": "SIMPLICIO_REMOTE_STUDIO_TOKEN"
    }
  ]
}
```

Rules enforced by both the TypeScript parser (`apps/desktop/src/remote_fleet.ts`)
and the native command (`apps/desktop/src-tauri/src/remote_fleet.rs`):

- `schema` is exactly `simplicio.desktop-remotes/v1`; unknown fields are errors.
- At most 32 remotes; `id` is lowercase `[a-z0-9._-]`, unique, up to 64 bytes.
- `url` is `http` or `https`, without userinfo, query or fragment. A trailing
  slash is normalized away. IPv6 and `localhost` loopback are supported.
- `token_env` names an environment variable (`[A-Z_][A-Z0-9_]*`). The token is
  read from the environment in the native process and is never written to the
  file or sent back to the WebView.
- A remote outside loopback is denied unless it declares `token_env`. Loopback
  may omit it, but then no token is sent and the machine is never actionable.
- Values that look like literal credentials are refused, and a `token` field is
  rejected instead of ignored.

An absent file is an empty fleet, not a demo. An unreadable or invalid file is
an empty fleet plus a reason code; the Desktop does not invent machines.

## Probe contract

For each configured remote the native command performs one
`GET <url>/v1/health` with `Authorization: Bearer <token>` when a token is
configured, a 3s timeout, redirects disabled and a 64 KiB body cap. The
expected body is:

```json
{ "status": "ok", "version": "3.10.0" }
```

An optional `workers` array carries the read-mostly worker list for the mobile
layout. It is bounded to 32 entries and fails the whole machine (reason
`remote_workers_invalid`) instead of publishing a partial row:

```json
{
  "status": "ok",
  "version": "3.10.0",
  "workers": [
    {
      "id": "w-1",
      "label": "issue-468",
      "claim": "issue:468",
      "state": "running",
      "progress": { "done": 3, "total": 7 },
      "receipt_id": "rcpt-468-abc"
    }
  ]
}
```

`id` is `[A-Za-z0-9][A-Za-z0-9._:-]{0,63}`, unique per machine; `label` is up
to 80 characters; `claim` up to 120; `state` is one of `queued`, `running`,
`paused`, `blocked`, `done`; `progress.done` <= `progress.total` (or `total`
absent when the remote does not know it); `receipt_id` is the Runtime's bounded
receipt. An absent list means "no workers reported", never "unknown".

Status mapping:

| Observation                    | `status`       | `authenticated` |
| ------------------------------ | -------------- | --------------- |
| 2xx with `status: ok/healthy`  | `online`       | true only if a token was sent |
| 401 or 403                     | `unauthorized` | false           |
| other HTTP status              | `offline`      | false           |
| timeout, DNS or connect error  | `offline`      | false           |
| 2xx without a valid body       | `offline`      | false           |
| `token_env` unset or unusable  | `unauthorized` | false           |

The projection is `simplicio.desktop-remote-fleet/v1` and contains only `id`,
`label`, `url`, `status`, `authenticated`, `version`, `latencyMs`, `reasonCode`
and `workers` (bounded worker entries with `id`, `label`, `claim`, `state`,
`progress` and `receiptId`). The command requires fresh Runtime authorization,
like the other read commands.

## Authorization model

- The config file is an allowlist: nothing is discovered on the LAN.
- Tokens live only in the user's environment. They are resolved inside the Rust
  command, used for a single request and dropped; they are not persisted,
  logged or returned over IPC.
- The panel enables per-machine controls only when `status === "online"` and
  `authenticated === true`. The control itself is a local selection, not a
  remote effect. Steering actions require their own authorized command and are
  not implemented here.
- Diagnostics are redacted before rendering (`redactRemoteText`).

## Mobile view

The same projection renders as a read-mostly layout for a narrow Desktop window
(<= 480 px). It is a layout of the Desktop window, not a mobile app or build:
`docs/desktop/REMOTE-FLEET.md` still makes no claim that a phone client exists.

- `apps/desktop/src/mobile_fleet.ts` builds `simplicio.desktop-mobile-fleet/v1`
  from the fleet the panel already loaded. It performs no fetch, so the mobile
  layout cannot issue a second fleet query.
- `buildMobileFleet(fleet, width)` is a pure function; the breakpoint is
  `fleetLayoutMode(width)` with a single boundary at `MOBILE_FLEET_MAX_WIDTH`
  (480 px). `RemoteFleetPanel` reads `window.innerWidth` once and re-renders the
  compact view at or below that width.
- Widths pinned by tests: **375 px** and **480 px** (plus 320, 481 and 1024 for
  the boundary itself).
- No horizontal scroll is a layout contract, not a promise: every grid track in
  `mobile_fleet.css` is `minmax(0, 1fr)`, the panel sets `max-width: 100%` and
  `min-width: 0`, and urls, ids, claims and receipts use
  `overflow-wrap: anywhere`. `src/mobile_fleet.test.ts` asserts those rules
  against the sheet and `e2e/mobile-fleet.spec.ts` measures
  `scrollWidth <= clientWidth` in Chrome at 375 px and 480 px.
- The narrow layout shows machines, workers, claims, progress and receipts. A
  remote that reports no workers shows "Nenhum worker reportado por esta
  máquina"; nothing is inferred from a neighbouring machine or from the local
  activity snapshot.

## Steering contract

The only remote effect this version sends is **pause or resume one worker**. It
is hidden unless the machine is `online` and `authenticated` (the token was
accepted), and the action is offered only for a worker in the matching state.

```
POST <url>/v1/workers/<worker_id>/pause
POST <url>/v1/workers/<worker_id>/resume
Authorization: Bearer <token from token_env>
```

Response (`simplicio.desktop-fleet-steer/v1` on the Desktop side):

```json
{ "worker_id": "w-1", "receipt_id": "rcpt-468-abc" }
```

Rules enforced by `apps/desktop/src-tauri/src/fleet_steer.rs`:

- The machine must be in the allowlist; a URL or token from the WebView is never
  accepted. `machineId` and `workerId` are validated (`[A-Za-z0-9][A-Za-z0-9._:-]*`,
  worker id <= 64 bytes) and the worker id is percent-encoded into one path
  segment.
- The token is resolved in-process from `token_env`. Without it no request is
  sent and the answer is `fleet_steer_unauthorized`; a machine without
  `token_env` (loopback) is readable but never steerable.
- `POST` only, 3s timeout, redirects disabled, 16 KiB body cap, no retry.
- `401`/`403` -> `fleet_steer_unauthorized`; other non-2xx ->
  `fleet_steer_remote_error`; network failure -> `fleet_steer_unreachable`.
- A `2xx` without a bounded `receipt_id` -> `fleet_steer_receipt_missing`. The
  Desktop never mints a receipt: the id in the answer is the Runtime's, the same
  one its event stream puts in the activity timeline.
- The Tauri command `desktop_fleet_steer` additionally requires active access on
  this device, and `mobile_fleet.ts` refuses to project a control for a machine
  that is not online+authenticated.

## Validation

- `npm test` in `apps/desktop` (full suite) covers the projection, the
  breakpoint, the component at 375/480 px, the bridge and the Rust-mirroring
  parser. `src/mobile_fleet.test.ts` also pins the CSS contract.
- `npx playwright test e2e/mobile-fleet.spec.ts` measures the real layout at
  375 px and 480 px (`document.documentElement.scrollWidth <= innerWidth`, panel
  `scrollWidth <= clientWidth`) and asserts the controls exist only for the
  online machine.
- `TAURI_CONFIG='{"bundle":{"externalBin":[]}}' cargo test --lib remote_fleet`
  and `cargo test --lib fleet_steer` in `apps/desktop/src-tauri`. The
  `fleet_steer` tests include a one-request loopback server that answers `401`
  to a tokenless `POST`, which is the API proof that an unauthenticated steering
  call is rejected; no test in this repo contacts a real remote runtime.
- `npm run build` type-checks the panel, the bridge and the mobile layout.
