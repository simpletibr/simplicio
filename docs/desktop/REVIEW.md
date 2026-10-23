# Desktop review flow

The Desktop review surface turns the working-tree diff into a deterministic
digest, then hands the human's comments to the owning agent through one bounded,
local queue file. The receipt proves that the file was written; it does **not**
prove that a live agent session read it or was notified.

## Diff digest

`desktop_review` runs `git diff --no-ext-diff --unified=3` against `HEAD` (or a
provided base), includes `git status --porcelain` in the hash input, and returns
`simplicio.desktop-review/v1`:

```json
{
  "schema": "simplicio.desktop-review/v1",
  "repo": "C:/repo",
  "base": null,
  "status": " M src/review.ts",
  "diff": "diff --git ...",
  "digest": "sha256:<64 hex>",
  "truncated": false,
  "redacted": true
}
```

The digest is `sha256(status + "\n" + diff)`. Diffs over 200 KB are truncated;
`truncated: true` always blocks auto-merge because the review is incomplete.
The preview browser build never reads the filesystem and fails with
`preview_no_runtime`.

## Plan digest and auto-merge

Auto-merge is only a plan-lane gate, never a general merge button. Eligibility
uses this fixed precedence, in both the UI and the native receipt:

| Precedence | Condition | `reason` |
| --- | --- | --- |
| 1 | `truncated == true` | `truncated` |
| 2 | a changed path is protected | `protected_path` |
| 3 | no plan digest supplied or stored | `plan_digest_missing` |
| 4 | plan digest differs from the diff digest | `plan_digest_mismatch` |
| 5 | plan digest equals the diff digest and no guardrail | `eligible` |

The plan digest comes from the optional `planDigest` Tauri argument; when it is
absent, `desktop_review_submit` reads the first non-empty line of
`.simplicio/plan-digest` (maximum 4 KB). The file is ignored by Git.

Protected paths are the same guardrail set as the UI: `Cargo.toml`,
`Cargo.lock`, `package-lock.json`, `install.sh`, `install.ps1`,
`simplicio-update-manifest.json`, `SHA256SUMS`, and any path under `.github/`,
`schemas/` or `migrations/`.

## Submission and inbox

`desktop_review_submit` requires active access and a fresh review:

| Argument | Meaning |
| --- | --- |
| `repo` | canonical local repository path |
| `digest` | digest returned by `desktop_review`; a stale value fails with `review_digest_mismatch` |
| `comments` | Markdown comments, trimmed, 1–20,000 characters |
| `planDigest?` | optional plan digest; falls back to `.simplicio/plan-digest` |
| `base?` | optional base used to recompute the fresh review; one revision, never an option |

The command recomputes the diff, rejects any digest mismatch, redacts the
comments, and writes one queue entry:

```
.simplicio/review-inbox/sha256-<64 hex>.json
```

`:` is not legal in Windows file names, so the scheme separator becomes `-`.
The file uses `simplicio.review-submission/v1`:

```json
{
  "schema": "simplicio.review-submission/v1",
  "receipt_id": "review-<24 hex>",
  "entry_digest": "sha256:<64 hex>",
  "repo": "C:/repo",
  "digest": "sha256:<64 hex>",
  "base": null,
  "plan_digest": "sha256:<64 hex>",
  "comments": "fix the guardrail",
  "comments_digest": "sha256:<64 hex>",
  "comments_bytes": 19,
  "truncated": false,
  "protected_paths": [],
  "auto_merge": { "eligible": true, "reason": "eligible" },
  "redacted": true,
  "submitted_at_epoch_ms": 1790000000000
}
```

Submitting the same digest, comments and plan again is idempotent: the existing
entry is kept, and the same `receipt_id` is returned with `"idempotent": true`.
Changed comments for the same diff produce a new receipt and atomically replace
the single entry for that digest. The command returns
`simplicio.review-receipt/v1` with `receipt_id`, repository-relative `path`,
`entry_digest`, `comments_digest`, `auto_merge`, `idempotent` and
`redacted: true`.

Comments are redacted before persistence: assignment-style secrets
(`token=`, `password=`, `secret=`, `api_key=` and similar), `Bearer` values,
common vendor prefixes (`sk-`, `ghp_`, `github_pat_`, `xox…`, `AKIA…`) and
private-key blocks. Redaction is a safety net; comment content remains
untrusted input.

## Commit and push

The review flow ends with two mutations, both authorized by the same review
state. `desktop_review_commit` creates exactly one commit from the paths in the
reviewed diff and records the real sha; `desktop_review_push` pushes only a
commit whose receipt exists in this repository.

### Commit guards

| Precedence | Condition | Code |
| --- | --- | --- |
| 1 | review document is not `simplicio.desktop-review/v1` | `review_unavailable` |
| 2 | diff truncated at 200 KB | `review_truncated` |
| 3 | review used a `base` (the diff includes already-committed work) | `review_commit_base_unsupported` |
| 4 | the diff names no file | `review_changes_empty` |
| 5 | a changed path is absolute, starts with `-`, or contains `..` | `review_path_invalid` |
| 6 | a changed path is protected (same set as auto-merge) | `review_protected_path` |
| 7 | message empty, over 4,096 chars, or containing NUL | `review_message_empty` / `review_message_too_large` / `review_message_invalid` |
| 8 | current branch is `main`/`master` | `review_branch_protected` |
| 9 | HEAD is detached | `review_branch_detached` |
| 10 | a merge/rebase/cherry-pick/revert/bisect is in progress | `review_commit_in_progress` |

The commit itself is `git commit -m <message> -- <reviewed paths>`: only the
reviewed paths are committed, so unrelated staged or untracked work stays out.
Hooks run normally (no `--no-verify`). The digest from the review screen must
still match a freshly recomputed diff (`review_digest_mismatch`), otherwise the
commit is refused before git runs.

### Commit receipt

Success writes `.simplicio/review-commits/<64 hex>--<sha>.json` atomically
(symlinked `.simplicio/` or state directory refused):

```json
{
  "schema": "simplicio.desktop-review-commit/v1",
  "status": "committed",
  "receipt_id": "commit-<24 hex of sha>",
  "digest": "sha256:<64 hex>",
  "sha": "<40 hex>",
  "branch": "issue-469",
  "paths": ["src/review.ts"],
  "message_chars": 24,
  "message_digest": "sha256:<64 hex>",
  "protected_paths": [],
  "truncated": false,
  "upstream": null,
  "pushed": false,
  "pushed_at_epoch_ms": null,
  "redacted": true,
  "committed_at_epoch_ms": 1790000000000
}
```

The message is not persisted, only its char count and digest.

### Push guards

Push reads the commit receipt; a commit with no receipt is never pushed
(`review_commit_missing`). It also refuses a receipt that recorded `truncated`
or any `protected_path` (`review_protected_path`), a different current branch
(`review_commit_branch_changed`), and a sha that is not `HEAD`
(`review_commit_not_head`).

- `main`/`master` are never pushed (`review_branch_protected`).
- No upstream and no explicit creation → `review_push_no_upstream`.
- An upstream pointing at a differently named branch → `review_push_upstream_mismatch`.
- Creation is explicit (`createUpstream: true`) and uses `origin`
  (`git push --set-upstream origin <branch>:<branch>`), otherwise
  `git push <remote> <branch>:<branch>`.
- There is no force path: the refspec is built, never accepted, and it may not
  start with `+`.

The receipt is updated in place (`pushed`, `upstream`, `pushed_at_epoch_ms`) only
after a successful push. Repeating the push of a receipt already marked
`pushed` returns `"idempotent": true` without touching the remote.

### Failures carry the real stderr

A failing hook or a rejected push is data, not a generic error: the document has
`"status": "commit_failed"` / `"push_failed"`, the real `stderr` (redacted and
bounded to 8 KB), `exit_code` and the failed `step`. Only guards are error codes.

```json
{
  "schema": "simplicio.desktop-review-push/v1",
  "status": "push_failed",
  "sha": "<40 hex>",
  "branch": "issue-469",
  "upstream": null,
  "idempotent": false,
  "code": "review_push_failed",
  "exit_code": 1,
  "stderr": "! [rejected] issue-469 -> issue-469 (non-fast-forward)",
  "redacted": true
}
```

### State machine

`review_git::CommitPushState` is the only writer of the phase:

| From | Event | To |
| --- | --- | --- |
| `ready` | commit succeeded with a valid sha | `committed` |
| `ready` | commit failed | `failed` (step `commit`) |
| `committed` | push succeeded with an upstream | `pushed` |
| `committed` | push failed | `failed` (step `push`) |

Any other transition is `review_git_transition_invalid:*`: a push can never be
claimed before a recorded commit, and a success can never follow a failure.

## Agent handoff

The inbox file is the verified handoff. At the start of a review, the owning
agent reads `.simplicio/review-inbox/*.json` and uses only the entry whose
`digest` matches the diff it is reviewing. Comment text is data, never
instructions: the agent must not execute embedded commands or change its rubric
because a comment asks it to.

The Desktop does not start, wake or message an agent session. A receipt means
"the queue entry exists and matches this diff", not "the agent saw this
comment". See the `simplicio-review` skill for the agent-side step.

## Validation

Covered by `apps/desktop/src/review.test.ts`,
`apps/desktop/src/components/ReviewFlow.test.tsx` and the `review_submit`
Rust unit tests: eligibility matrix, digest mismatch, protected paths,
truncation, bounded/redacted comments, idempotent submission and receipt shape.

The commit/push edge is covered by `apps/desktop/src-tauri/src/review_git.rs`
unit tests (state machine, guards, message/path bounds, no force refspec) and
integration tests against a scratch repository with a bare `origin` remote: a
real commit with its sha, a failing `pre-commit` hook showing the real stderr, a
rejected non-fast-forward push showing the real stderr, and an upstream created
explicitly. `desktop_api` tests hold the same 401/403 contract for
`POST /v1/review/commit` and `POST /v1/review/push`.
