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
