# Scripted Desktop API (local, authenticated)

Status: implemented in `apps/desktop/src-tauri/src/desktop_api.rs` for the
scripting groups of the twin `simplicio desktop <group> <action>` and the
`simplicio_desktop` MCP tool (#439). The Runtime side of the twin is still Slice 1
(`desktop_api_not_implemented` when a Desktop is reachable); this document is the
Desktop half of that contract.

The API binds an ephemeral loopback port at startup, writes a discovery file and
requires a bearer token on every route.

```
$HOME/.simplicio/desktop-api.json      mode 0600, atomic write
{ "schema": "simplicio.desktop-api/v1", "host": "127.0.0.1", "port": <p>, "token": "<64 hex>" }
```

Responses are always `simplicio.desktop-api-response/v1`:

```json
{ "schema": "simplicio.desktop-api-response/v1", "status": "ok",    "data": { } }
{ "schema": "simplicio.desktop-api-response/v1", "status": "error", "error": { "code": "<stable_code>" } }
```

| Condition | Status |
| --- | --- |
| No `Authorization` header | `401 unauthorized` + `WWW-Authenticate: Bearer` |
| Header present but not `Bearer <token>` / wrong token | `403 forbidden` |
| Unknown query key, ambiguous `selector` + `repo`, bad `wait` | `400 invalid_query` |
| Unknown path | `404 not_found` |
| Known path, wrong method | `405 method_not_allowed` |
| Runtime/receipt/report unavailable, access unverified | `503` |

The token is compared without an early return and is never logged, returned by
`desktop_api_status`, or echoed in a response body.

## Selectors

`selector=<kind>:<value>`, parsed exactly like the Runtime twin
(`DesktopSelector::parse`). A value without a prefix is rejected; it is never
guessed.

| Selector | Grammar | Rejected examples |
| --- | --- | --- |
| `id:<x>` | non-empty, no whitespace, no control characters | `run-7`, `id:`, `id:a b` |
| `path:<p>` | non-empty path to an existing directory (canonicalized) | `path:`, a missing path, a file |
| `issue:<n>` | `n` is a `u64`; `0` resolves to `issue_invalid` | `issue:x`, `issue:` |

`<kind>:<value>` is echoed back in every scripted document as
`{"raw":"issue:439","kind":"issue","value":"439"}`.

`issue:<n>` and `id:<x>` are resolved against `git worktree list --porcelain`
of the `repo` parameter (or the default repository): a worktree matches when its
branch (`issue-439`) or its directory name (`issue-439`) equals the value. No
match is `404 worktree_not_found`.

## Routes

| Route | Twin command | Response `data.schema` |
| --- | --- | --- |
| `GET /v1/health` | `status` | `simplicio.desktop-api/v1` |
| `GET /v1/snapshot` | `snapshot` | Runtime snapshot |
| `GET /v1/report?repo=` \| `?selector=` | `report open <sel>` | Runtime execution report |
| `GET /v1/review?repo=&base=` | (review screen) | `simplicio.desktop-review/v1` |
| `POST /v1/review/commit` | (review screen) | `simplicio.desktop-review-commit/v1` |
| `POST /v1/review/push` | (review screen) | `simplicio.desktop-review-push/v1` |
| `GET /v1/worktrees?repo=` | `worktree ps` | `simplicio.desktop-worktrees/v1` |
| `POST /v1/worktree?repo=` | `worktree create --issue <n>` | `simplicio.desktop-worktree-create/v1` |
| `GET /v1/run?selector=` (or `POST`) | `run open <sel>` | `simplicio.desktop-run/v1` |
| `GET /v1/run?selector=&wait=idle` | `run wait <sel> --for idle` | `simplicio.desktop-run/v1` |
| `GET /v1/diff?selector=&base=` | `diff open <sel>` | `simplicio.desktop-diff/v1` |
| `GET /v1/receipt?selector=id:<run>` | `receipt open <sel>` | `simplicio.desktop-receipt/v1` |

`desktop_api::ROUTES` is the single table for path, methods and accepted query
keys; dispatch, `404`, `405` and `invalid_query` all read it, so a route cannot
be registered halfway.

### `/v1/run`

`id:<goal>` runs `simplicio goal report [--repo <p>] --id <goal> --json`.
`path:` reads the overview for that directory; `issue:` reads the overview of the
managed worktree. `POST` accepts the same fields as a JSON body
(`{"selector": "...", "wait": "idle", "repo": "..."}`); a selector in both the
query and the body is `400 invalid_query`.

`wait=idle` polls the same report until the run is no longer active
(`/goal/status`, `/status` or `/loop/status` in
`complete|completed|done|failed|cancelled|canceled|idle`) or the bounded budget
(5 attempts, 200 ms apart, ≤ 1 s) is spent. The last document is always returned;
the outcome is data, not an HTTP error:

```json
{ "schema": "simplicio.desktop-run/v1", "group": "run", "action": "wait",
  "selector": { "raw": "id:run-7", "kind": "id", "value": "run-7" },
  "repo": null, "goal_id": "run-7",
  "wait": { "for": "idle", "outcome": "idle", "attempts": 2, "elapsed_ms": 21 },
  "run": { "schema": "simplicio.goal-report/v1" } }
```

`outcome` is `timeout` when the budget is spent; `attempts` and `elapsed_ms`
make the budget auditable.

### `/v1/review/commit` and `/v1/review/push`

Both are `POST` with a JSON body and no query keys; a query key is
`400 invalid_query`. `repo` is required in the body: a mutation is never sent to
a guessed default repository.

```json
POST /v1/review/commit
{ "repo": "/tmp/wt-469", "digest": "sha256:<64 hex>", "message": "feat: x", "base": null }
```

The digest must still match a freshly recomputed `git diff` (otherwise
`409 review_digest_mismatch`); the guards, the receipt and the state machine are
documented in `docs/desktop/REVIEW.md`. A failed hook is **not** an HTTP error:
the route answers `200` with `status: "commit_failed"` and the real `stderr`, so
the script sees exactly what git wrote.

```json
POST /v1/review/push
{ "repo": "/tmp/wt-469", "digest": "sha256:<64 hex>", "sha": "<40 hex>", "createUpstream": false }
```

`createUpstream` (alias `create_upstream`) is the explicit upstream creation;
without it a branch with no upstream is `409 review_push_no_upstream`. There is
no force flag and unknown body fields are `400 invalid_json`.

### `/v1/diff`

Resolves the selector to one working tree and returns the same bounded, redacted
`git diff` as the review screen (`crate::diff_snapshot`, 200 000-byte clamp,
`sha256:` digest, `truncated`). `base` is validated by the same rule as review
(`review_base_invalid`).

### `/v1/receipt`

A receipt is addressed by run id, so only `id:<run>` is accepted.
`path:`/`issue:` answer `400 selector_kind_unsupported` instead of guessing which
receipt of that worktree was meant. The receipt itself comes from
`simplicio evidence receipt get --run-id <id> --json`.

### `/v1/report`

Without a selector the route keeps its `repo`-only contract. With a selector:
`id:` becomes the run filter (the optional `repo` still narrows the query),
`path:` is the repository itself, and `issue:` uses `repo` as the base
repository for the worktree lookup. `path:` together with `repo` is
`400 invalid_query` on every scripted route, because the path already names the
working tree.

## Error codes

| Code | Status |
| --- | --- |
| `invalid_json`, `invalid_query`, `invalid_repo`, `repo_path_invalid`, `issue_invalid`, `agent_invalid`, `invalid_selector`, `selector_required`, `selector_kind_unsupported`, `review_base_invalid`, `review_digest_invalid`, `review_message_empty`, `review_message_too_large`, `review_message_invalid`, `review_commit_sha_invalid` | 400 |
| `desktop_access_not_active` | 403 |
| `worktree_not_found` | 404 |
| `wip_limit_reached`, `worktree_exists`, `worktree_path_invalid`, `review_digest_mismatch`, `review_truncated`, `review_protected_path`, `review_changes_empty`, `review_path_invalid`, `review_branch_protected`, `review_branch_detached`, `review_commit_base_unsupported`, `review_commit_in_progress`, `review_commit_missing`, `review_commit_not_head`, `review_commit_branch_changed`, `review_commit_receipt_invalid`, `review_push_no_upstream`, `review_push_upstream_mismatch`, `review_push_upstream_invalid`, `review_push_refspec_invalid` | 409 |
| `run_unavailable`, `receipt_unavailable`, `execution_report_unavailable`, `desktop_access_unverified`, any `runtime_*` | 503 |

## Tests

```bash
cd apps/desktop/src-tauri
TAURI_CONFIG='{"bundle":{"externalBin":[]}}' cargo test --lib desktop_api
```

`TAURI_CONFIG` removes the packaged-sidecar requirement from the build script;
the suite does not execute a Runtime. `desktop_api::ScriptedActions` is the seam:
the native implementation is the seven Runtime/git calls above, and the tests use
canned documents to exercise authentication, selector resolution, the `wait`
budget, the review commit/push body contract and every error mapping over a real
loopback socket. `diff_snapshot` is additionally tested against a throwaway git
repository, so the diff text is real.
