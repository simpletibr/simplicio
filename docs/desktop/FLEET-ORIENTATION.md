# Fleet orientation: measuring the first worktree orientation (#433)

The fleet cockpit gives every task its own worktree. This document covers the
second half of the #433 contract: the **first orientation of each worktree**
must come from the shared default-branch baseline and its duration must be
measured, never guessed.

## Path

```
FleetCockpit "Criar worktree" / "Adicionar à fila"
  → bridge.createDesktopWorktree / bridge.orientDesktopWorktree
  → Tauri desktop_worktree_create / desktop_worktree_orient
  → orient_worktree (src/lib.rs)
  → worktree_orientation::orient (src-tauri/src/worktree_orientation.rs)
  → `simplicio map --repo <worktree> --json` (Runtime owns the baseline)
  → receipt.orientation → fleet task `orientation_ms` → board
```

`create_managed_worktree` still creates a real git worktree and still returns
`status: created`. The orientation is an extra field of the same receipt, and a
failure to measure never fails creation.

The `orientation` object is also what the local API returns from
`POST /worktree`, because `desktop_api` returns the same create receipt
unchanged.

## How the baseline is consumed

`simplicio-runtime#6594` already maps the default branch once per commit and
stores the result in `<git-common-dir>/simplicio/map`, shared by every
worktree of the repository. The Desktop does not remap anything:

1. **Probe.** `worktree_orientation::baseline_store_ready` reads
   `<git-common-dir>/simplicio/map` for a stored `baseline-<tree>.json`. No
   stored baseline means the answer is `baseline_missing` and the Runtime is
   not invoked at all — opening a task never triggers a full map.
2. **Ask.** `simplicio map --repo <worktree> --json` is bounded (10 s) and its
   last JSON line is parsed. The Runtime resolves `baseline =
   merge-base(HEAD, default branch)` and serves `baseline + delta`.
3. **Classify** from the receipt, never from an assumption:

   | `receipt.cache_state` | Meaning | Status |
   | --- | --- | --- |
   | `hit` | Served from the stored baseline, nothing remapped | `measured` |
   | `written` / `miss` | This call built the baseline | `baseline_missing` |
   | `stale` | Another generation was served | `stale` |
   | — (nonzero exit, unreadable JSON) | — | `map_failed` / `timeout` / `unavailable` |

4. **Measure.** `orientation_ms` is the wall time of the invocation, measured
   with `Instant` around the call. `baseline_build_ms` is the build time stored
   with the baseline (the Runtime's own `elapsed_ms`); on a `hit` it does *not*
   describe this call, so it is reported under its own name.

`within_budget` is always derived from the measured number (`< 2000 ms`) in
both Rust and TypeScript, so a payload cannot claim the budget while reporting
a longer duration.

## What the UI shows

- A task with a real measurement renders the number (`412 ms`) in the lane card.
- A task without one renders `orientação não medida`, and the cockpit prints
  the actionable reason (`baseline_missing`, `stale`, `timeout`,
  `unavailable`, `map_failed`) instead of a duration.

## Reproducing the measurement

Unit tests (no Runtime needed):

```
cd apps/desktop/src-tauri
cargo test --lib worktree_orientation
```

Integration measurement with the real Runtime (creates a shared clone of a
repository, primes its baseline once, then orients two fresh worktrees):

```
cd apps/desktop/src-tauri
SIMPLICIO_RUNTIME_BIN=$(command -v simplicio) \
  cargo test --lib measured_worktree_orientation -- --ignored --nocapture
```

Add `SIMPLICIO_ORIENTATION_SOURCE_REPO=<repo>` to measure a large real
repository instead of the 40-file fixture.

## Measured results

Command (the same code path the Desktop command runs):

```
cd apps/desktop/src-tauri
SIMPLICIO_RUNTIME_BIN=$(command -v simplicio) \
  SIMPLICIO_ORIENTATION_SOURCE_REPO=<repo> \
  cargo test --lib measured_worktree_orientation -- --ignored --nocapture
```

| Scenario | First orientation | Second orientation | Baseline |
| --- | --- | --- | --- |
| 40-file fixture (`cache_state: hit`, `generation: baseline`) | 295 ms | 297 ms | reused |
| `simpletibr/simplicio`, 673 files, run 1 | 1041 ms | 965 ms | reused |
| `simpletibr/simplicio`, 673 files, run 2 | 820 ms | 1201 ms | reused |
| `simpletibr/simplicio`, 6 fresh worktrees in a row (load ≈ 20) | 610–1098 ms | — | reused |
| `simpletibr/simplicio`, warm repeats in one worktree | 389–801 ms | — | reused |

Two outliers of 9.8 s and 18.2 s were observed while ten `rustc` processes from
unrelated local builds were running (load average ≈ 25). In those runs the
parent process spent ≈0.00 s in user and ≈0.03 s in system time with thousands
of involuntary context switches: it was waiting, not mapping, and the Runtime
still reported `cache_state: hit`. The six consecutive fresh worktrees under
load ≈ 20 (the table above) are the representative measurement; the outliers
are recorded here instead of being silently dropped.
