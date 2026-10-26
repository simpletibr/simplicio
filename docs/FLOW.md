# The delivery flow (measured 2026-10-26)

One page, from a one-line task to merged code. The flow picks the cheapest path that still proves itself; every number is from a run on this host, recorded in `benchmarks/2026-10-26-codegen-create-edit.md` and `benchmarks/2026-10-26-shape-selector.md`.

## The nine steps

| # | step | command | measured | when |
|---|---|---|---|---|
| 0 | **shape** | `shape "<task>" --json` | 138 ms p50 local, 215 ms with JEV, 0 tokens | always |
| 1 | **contract** | `codegen infer --repo .` (background) | 0.79 s | no contract in the repo |
| 2 | **create** | `codegen generate --schema … --mode/--preset` | **96-235 ms, 16-27 files, 0 tokens** | creation, or a feature with a contract |
| 3 | **implement the seam** | model writes `App.impl.tsx` / `IApiService` | one file, the only model-authored file | after generate |
| 4 | **edition** | edit the contract, then `codegen sync --check` -> `sync` (bound) or `generate` again | **110-223 ms, 9-22 files, 0 tokens** | any contract change |
| 5 | **verify** | `sync --check` (exit 1 = drift), project tests, `edit` receipt | 0.1-0.3 s | always, same turn |
| 6 | **record** | `learn from-run` / `precedent` / `memory-v2 store` | 0.1-0.2 s | after the task, not before |
| 7 | **publish** | branch + PR with the receipt | — | when the work is proven |
| 8 | **escalate** | `levi acquire` / `bot-do` | network / reflex | only on the conditions below |

`shape` decides between the two programming paths:

- `shape: mcp` + a contract or the codegen lane -> steps 1-5 (generate, implement the seam, sync).
- `shape: native` -> a named change with no contract: read the file, `edit`, verify. Do not generate for a one-file change; measured 3.42x cheaper over a create+edit session.

## Why codegen is the only path that scales

| path | wall | files landing | tokens | cost |
|---|---|---|---|---|
| codegen create (advanced React) | **96 ms** | 27 | 0 | $0 |
| codegen edition (advanced React, new entity) | **128 ms** | 22 | 0 | $0 |
| codegen edition (C# bound output) | **114-157 ms** | 3 (+2 receipts) | 0 | $0 |
| model edits 2 files (same host, in-session A/B) | **13.19 s** | 2 | 1,973 in + 861 out | $0.001245 |

The model edits one file per turn and pays for the context each time; the generator writes every derived file in one pass from the contract. The model's job shrinks to two things a generator cannot do: **writing the contract** (or `infer` when there is none) and **implementing the one handwritten seam** that every regeneration preserves.

## Map: one per generation, reuse the slice

| step | wall | rule |
|---|---|---|
| `map` cold | 213-376 ms | once per repository generation |
| `map` warm | 178-249 ms | cache hit; never a substitute for `context` |
| `context --term` | 196 ms (74 ms with the resident daemon) | the bounded slice you actually read |
| `project-map.json` | 4.8-5.7 KB | 42x smaller than `grep -rn` + `cat` |

**Do not map a codegen task.** The contract is the orientation and it is already exact; every creation number above ran without a map. Map is for the `native` and `mcp` navigation paths, once, then reuse it through `context`.

## The optional layers, and when they pay

| layer | use it | do not use it |
|---|---|---|
| **JEV** (plugin, backend `typesafe`, gate p >= 0.8) | only when rules + task class abstain; `shape` reports `gate: accepted\|below_0.8` | as an always-on route: +3.2 pp lane+risk for 2x p50 and one network call per undecided task; use `--no-jev` for bulk runs |
| **memory / database** (SQLite FTS5, 1,690 items; `memory-v2`, `precedent`) | after the task: store shape -> outcome, codegen target, drift verdict; retrieve precedents when a new task looks familiar | in the hot path: 0.1-0.2 s per call buys nothing while the task is still open |
| **simplicio-bot** (reflex procedures) | repeated identical operations with a stored procedure and a proven record | codegen work: the generator is already deterministic, faster and free |
| **levi** (gated external knowledge) | only after project memory and runtime knowledge miss **and** the gap is external and current (a library or API fact) | as a first step, or for anything the repo/contract already answers |
| **daemon** | an interactive session with many context/tool calls: `context` 74 ms vs 196 ms | one-shot CLI batches: start costs 341-458 ms and the total flow is unchanged (-0.8%) |
| **CPU executor** | MCP/agent bulk: cold call p50 113.6 ms, resident 5-slot p50 343 us at 6,142 calls/s | a single CLI generate: in-process Rust, no executor round trip needed |

## What to do with what we learn

1. **Store the verdict, not the transcript**: task shape, chosen path, files landed, drift result, test result. That is what makes the next `shape` cheap and the next precedent reusable.
2. **Keep the learning out of the hot path**: 0.1-0.2 s per memory call is 100x the cost of the `shape` call it would inform.
3. **Never learn from an unverified run**: a red test or an unmerged branch is not a precedent.

## Known gaps (measured)

1. `--mode work-with` (React) writes **no codegen bindings**, so `sync --check` cannot gate it; the edition path is "generate again" (safe: `App.impl.tsx` is preserved by digest, verified).
2. `codegen sync --schema … --preset …` fails with `preset_contract_unparseable`; the binding path (`sync` with no arguments) works.
3. The `native` shape remains the right answer for a 1-3 file change with no contract: 3.42x cheaper than the governed session over create + edition.
