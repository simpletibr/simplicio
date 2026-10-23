---
name: simplicio-desktop
description: Script the running Simplicio Desktop through its local authenticated API. Use when an agent needs Desktop snapshots, execution reports, reviews, managed worktrees, or a health check without driving the UI.
---

# Simplicio Desktop API

Simplicio Desktop exposes a small, loopback-only HTTP API for the same actions
available from the Desktop commands. It is a local control surface for agents
and scripts; it does not replace the Simplicio Runtime MCP and it does not
change any third-party MCP server, plugin, or host integration.

## Discovery

The Desktop writes a discovery file at startup:

- Windows: `%USERPROFILE%\.simplicio\desktop-api.json`
- macOS/Linux: `$HOME/.simplicio/desktop-api.json`

The file uses `simplicio.desktop-api/v1`:

```json
{
  "schema": "simplicio.desktop-api/v1",
  "host": "127.0.0.1",
  "port": 51234,
  "token": "<random bearer token>"
}
```

The token is a secret. Read it from the file into a variable, never print it,
never commit it, and never pass it on a command line that is logged. The server
binds `127.0.0.1` on an ephemeral port and rejects every request without the
header.

The `desktop_api_status` Tauri command returns `schema`, `status`, `host` and
`port` only. It never returns the token.

## Authentication

Every endpoint requires:

```http
Authorization: Bearer <token>
```

- Missing header: `401 Unauthorized`
- Present but wrong token or wrong scheme: `403 Forbidden`

Responses use `simplicio.desktop-api-response/v1`:

```json
{ "schema": "simplicio.desktop-api-response/v1", "status": "ok", "data": {} }
```

```json
{ "schema": "simplicio.desktop-api-response/v1", "status": "error", "error": { "code": "repo_path_invalid" } }
```

## PowerShell

```powershell
$api = Get-Content "$env:USERPROFILE\.simplicio\desktop-api.json" -Raw | ConvertFrom-Json
$headers = @{ Authorization = "Bearer $($api.token)" }
$base = "http://$($api.host):$($api.port)"

Invoke-RestMethod -Uri "$base/v1/health" -Headers $headers
Invoke-RestMethod -Uri "$base/v1/snapshot" -Headers $headers
Invoke-RestMethod -Uri "$base/v1/report?repo=$([uri]::EscapeDataString($PWD.Path))" -Headers $headers
Invoke-RestMethod -Uri "$base/v1/review?repo=$([uri]::EscapeDataString($PWD.Path))" -Headers $headers
```

## Bash

```bash
API_FILE="$HOME/.simplicio/desktop-api.json"
HOST=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["host"])' "$API_FILE")
PORT=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["port"])' "$API_FILE")
TOKEN=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["token"])' "$API_FILE")

curl -fsS -H "Authorization: Bearer $TOKEN" "http://$HOST:$PORT/v1/health"
curl -fsS -H "Authorization: Bearer $TOKEN" "http://$HOST:$PORT/v1/snapshot"
curl -fsS -H "Authorization: Bearer $TOKEN" \
  "http://$HOST:$PORT/v1/report?repo=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))' "$PWD")"
```

## Endpoints

All repository values must be absolute, existing directories. Values are
URL-encoded. When `repo` is omitted, the API uses `SIMPLICIO_DESKTOP_REPO`,
then the user's home directory, matching the Desktop projection default.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/v1/health` | Process-local health and API metadata. Does not call the Runtime. |
| `GET` | `/v1/snapshot` | `simplicio.desktop-snapshot/v1` from the verified Runtime. |
| `GET` | `/v1/report?repo=...` | `execution-report show --json` for the repository. |
| `GET` | `/v1/review?repo=...&base=...` | Redacted git review with `simplicio.desktop-review/v1` digest. |
| `GET` | `/v1/worktrees?repo=...` | Managed worktree listing (`worktree list --porcelain`). |
| `POST` | `/v1/worktree?repo=...` | Create a managed worktree. |

### Create a worktree

The body accepts:

```json
{ "issue": 439, "agent": "subagent", "wipLimit": 4 }
```

`repo` may be supplied in the body (`repo`, `repoPath`, or `repo_path`) or as
the `repo` query parameter. Supplying both with different values is rejected.
`issue` and `agent` are required. The existing WIP limit validation applies.

```bash
curl -fsS -X POST "http://$HOST:$PORT/v1/worktree" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"issue":439,"agent":"subagent","wipLimit":4}'
```

The worktree is created under `~/.simplicio/worktrees/<repo>/issue-<n>` on
branch `issue-<n>`.

## Limits and failures

- Request headers and bodies are bounded to 8 KB each.
- Request I/O has a 10-second deadline; the server closes the connection after
  one response (`Connection: close`).
- Errors use fixed codes such as `invalid_request`, `invalid_query`,
  `repo_path_invalid`, `desktop_access_not_active`, `wip_limit_reached`,
  `worktree_exists`, and `runtime_install_required`.
- The API never returns or logs the bearer token.

## Scope

This API is an additional Desktop surface. Existing Tauri commands, the
Simplicio Runtime MCP, third-party MCP servers, plugins, and host integrations
keep their current behavior and permissions.
