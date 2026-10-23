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
`label`, `url`, `status`, `authenticated`, `version`, `latencyMs` and
`reasonCode`. The command requires fresh Runtime authorization, like the other
read commands.

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

The same projection is designed to be rendered read-mostly by a future mobile
client: machines, status, version and latency, with actions hidden unless the
remote is online and authenticated. This document does not claim that a mobile
app or build exists; the Desktop panel is the only implemented surface.

## Validation

- `npm test -- src/remote_fleet.test.ts src/remote_fleet.bridge.test.ts src/components/RemoteFleetPanel.test.tsx`
  in `apps/desktop`.
- `cargo test remote_fleet` in `apps/desktop/src-tauri` covers the native
  parser and status mapping without network access; it needs the platform
  linker/VC runtime libraries.
- `npm run build` type-checks the panel and bridge.
