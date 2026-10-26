# Fast path: the entry flow for any task

The order below is the cheapest measured path to a delivered task. Every number is from the 2026-10-26 measurements (`benchmarks/2026-10-26-*`), median of 3-5 reps, daemon off, no network.

## One-screen decision

```
task arrives
   │
   ├─ 0. classify (deterministic, 0.004 ms) ─────────────── lane?
   │
   ├─ A. greenfield, <=3 files, no navigation ──────────── native write + shell   (~24 s agent loop)
   ├─ B. known single file / small change ──────────────── read + edit            (~0.4 s tools)
   ├─ C. unknown repo or many files ────────────────────── map -> context(term)    (~0.6 s tools)
   ├─ D. contract already exists ───────────────────────── codegen -> edit -> test  (~0.4 s tools)
   ├─ E. >=2 independent units ─────────────────────────── plan --agents N -> CPU executor
   ├─ F. needs iteration / proof ───────────────────────── loop (fast-path first)
   └─ G. UI proof, JEV classification ──────────────────── video / jev (edges only)
```

## Step by step

| # | step | tool | measured cost | when |
|---|---|---|---|---|
| 0 | **classify** | `plan --mode decide` / router | **0.004 ms**, 0 tokens | always, before anything |
| 1 | **orient** | `map` | **0.34-0.37 s**, 4.5 KB | repo unknown, or >10 files involved |
| 2 | **narrow** | `context --term <t>` | **0.26-0.28 s**, 28.3 KB | instead of reading files; 42x less than `grep -rn` + `cat` (1.19 MB) |
| 3 | **create** | `codegen generate --schema ... --lang ... --repo .` | **0.01 s**, 2 files | a contract (OpenAPI/JSON Schema/SQL DDL/TypeSpec) exists |
| 4 | **edit** | `edit '<plan>' --repo . --json` | **0.36 s**, byte-identical result | any mechanical change; 7.75x faster than 3.9.2 |
| 5 | **verify** | `shell` / `exec` / `benchmark run` | **0.01 s** local shell · **0.42 s** benchmark suite | after every change, same turn |
| 5b | **run a Runtime surface** | `exec "<subcommand>"` | inherits the subcommand (0.01-0.4 s) | a Runtime command is needed and only a command string is available |
| 6 | **fan out** | CPU executor (`plan --agents N`, `benchmark mcp-cpu`) | **0.25-0.32 s** | >=2 independent units, no shared files |
| 7 | **iterate** | loop (fast-path -> converge) | per-iteration = 0.4-0.6 s of tools | the evidence gate is not met on the first pass |
| 8 | **prove** | video (hyperframes) | minutes (render) | only when the deliverable is visual |
| 9 | **classify hard cases** | JEV | **unmeasured** (blocked) | only after rules + task_class abstain |

## Task -> entry -> cost

| task shape | entry command | tool cost (measured) |
|---|---|---|
| new 2-3 file module, nothing to navigate | native `write` + `shell` | **~0.02 s** local (agent loop 23.7 s) |
| change one known function | `context --term` (or `read` if the file is small) + `edit` | **~0.6 s** |
| fix a bug in an unfamiliar tree | `map` -> `context --term` -> `edit` -> `shell` | **~1.0 s** |
| generate a client/server/UI from a contract | `codegen generate` -> contract impl edit -> `shell` | **~0.4 s** |
| N entities x M targets | `codegen generate` per target + `edit` for the impl | 0.01 s per target |
| batch of independent tasks | `plan --agents N` + CPU executor | 0.25-0.32 s scheduling |
| refactor with drift checks | `edit` plans + `codegen sync --check` | 0.36 s per plan |
| visual deliverable | loop + video evidence | render-bound (minutes) |

## Hard rules (when NOT to use a tool)

- **Do not orient a 3-file greenfield task.** Measured: the MCP arm cost **4.4x** more and took **4.2x** longer than native tools (`2026-10-26-ab-mcp-vs-native`), because there is nothing to bound.
- **Do not `read` a tree.** One `context` is 42x smaller than `grep -rn` + `cat` of the same matches.
- **Do not hand-edit a mechanical change.** `edit` is 0.36 s and produces the same bytes on every version.
- **Do not write code by hand when a contract exists.** Codegen is 0.01 s and 0 LLM tokens.
- **Do not fan out below 2 independent units.** The CPU executor costs 0.25-0.32 s to schedule; one unit is a loss.
- **Do not loop a one-shot.** The loop pays the evidence gate per iteration.
- **Do not call JEV** until it has a key and a measured p50; today it is unmeasured and not wired into `plan`.
- **Do not render video** unless the deliverable is visual; it is minutes, not milliseconds.

## The exact entry commands

```bash
# 0. classify (deterministic router, 0 tokens)
simplicio plan --mode decide "<task>" --repo . --json

# 1-2. orient and narrow
simplicio map --repo . --json
simplicio context --repo . --term "<symbol or phrase>" --json

# 3. create from a contract
simplicio codegen generate --schema api.yaml --lang rust --repo .

# 4. edit (mechanical, receipted)
simplicio edit '{"file":"src/x.rs","operations":[{"op":"replace","find":"a","with":"b"}]}' --repo . --json

# 5. verify
simplicio benchmark run --json          # 4 scenarios, 0.42 s
simplicio benchmark mcp-cpu --json      # CPU executor, 0.25-0.32 s

# 6. fan out
simplicio plan "<task>" --repo . --agents 4 --json

# 7. iterate
simplicio loop ...
```

The MCP twins are the same operations with the same contracts: `simplicio_context`, `simplicio_map`, `simplicio_codegen`, `simplicio_edit`, `simplicio_exec`, `simplicio_run`.

### `exec` — the gated router

`simplicio exec "<subcommand>"` runs a Runtime subcommand through the gate: no raw shell, no shell expansion, the argv is a Runtime command. It is the right call when a step needs a Runtime surface (`map`, `context`, `edit`, `codegen`, `benchmark`) but the caller only has a string — for example from an agent that cannot spawn processes directly. It is not a shell: use the native shell for arbitrary local commands (`pytest`, `cargo`, `git`), and `simplicio_exec` (MCP, `kind=argv`) when the host profile blocks native tools; that lane is restricted to `git`, `gh`, `cargo`, `python`, `python3`, `npm`, `pytest`.

## What still has to be fixed for this to be the fastest

1. **`plan` regressed**: 0.18 s (3.9.2) -> 0.48 s (3.10.2) -> 0.37 s (main). Step 0 is on every task, so this is the first thing to fix; target <=0.20 s.
2. **Context grew 2x**: 13.7 KB -> 28.3 KB and 0.09 s -> 0.28 s. Step 2 is on every non-trivial task; target back to ~14 KB.
3. **Auth lockout**: an expired token plus a fail-closed plugin left the host with zero working tools for ~2 h. The flow above assumes the tools answer; offline grace is a prerequisite, not a nicety.
4. **JEV**: needs `OPENCODE_API_KEY` (or typesafe/openrouter), an install, and a measured p50/accuracy before it can be the last hop of step 0.
5. **Flaky bin tests**: the verify step must be trustworthy without `--no-verify`.

## The floor

For a task that needs all of it - orient, narrow, create, edit, verify - the tool time on `main` today is **0.37 + 0.26 + 0.01 + 0.36 + 0.42 = ~1.4 s**. The agent loop around it (planning, tool calls, model latency) dominates: 23.7 s for the smallest task measured, 99 s when the model had to use MCP for a trivial one. The fastest flow is therefore the one that spends the fewest *agent turns*, not the fewest milliseconds: one orient, one edit, one verify, stop.
