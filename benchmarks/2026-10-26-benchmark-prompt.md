# The benchmark prompt (canonical, 2026-10-26)

The exact text to paste so a run stays comparable with the numbers already published in `2026-10-26-ab-create-edit.md`, `2026-10-26-codegen-create-edit.md` and `2026-10-26-sandbox-3.10.3.json`.

Four prompts: **arm M** (Simplicio MCP, codegen), **arm N** (native tools, no Simplicio), **throughput** (codegen across the four cases, daemon off and on), and the **scorer**. The operator prompt seeds the repositories; the rest is pasted into a session.

## What the benchmark answers

1. Does the MCP surface pay for itself on a task that creates and then edits, in **one session**? (arm M vs arm N)
2. What does codegen cost and produce, per target and fixture size? (throughput)
3. Does the shipped binary behave like the build it came from? (throughput run inside the sandbox environment)

## Conditions (a run that breaks one is invalid, not slow)

| condition | why |
|---|---|
| same model and variant in both arms, same host, sequential | otherwise the ratio measures the model, not the surface |
| one session per arm, creation and edition inside it | four sessions measure two agents, not a workflow |
| both arms seeded from the same fixture: `git init`, contract only | a pre-generated tree hands arm N the answer |
| arm M: only `simplicio_*` tools plus the `simplicio` binary | the arm is the surface |
| arm N: only native read/write/edit/shell/glob, never the `simplicio` binary | otherwise it is arm M with extra steps |
| JEV and daemon recorded per run, never changed mid-run | both are named in the output |
| wall = sum of assistant turn durations (active), never cell time | the arms run sequentially, so cell wall bills the wait |
| a failed step is recorded with its exit code, then the arm stops | an arm that improvises is not comparable |

## Fixtures

- `benchmarks/fixtures/openapi-small.yaml` - 2 entities, 2 routes, no enums or refs (**basic**).
- `benchmarks/fixtures/openapi-advanced.yaml` - 13 schemas, 8 routes, enums, `$ref`, paging, invoice/order/warehouse graphs (**advanced**).

The fixture is copied to `openapi.yaml` in the arm repository and is the only input. Nothing else is generated, described or hinted.

## Prompt 0 - operator (run once per arm, before the session)

```bash
REPO=/tmp/bench/arm-M/basic-react
FIXTURE=benchmarks/fixtures/openapi-small.yaml
mkdir -p "$REPO" && cd "$REPO" && git init -q .
cp "$FIXTURE" openapi.yaml
git add -A && git -c user.email=bench@local -c user.name=bench commit -qm seed

export SIMPLICIO_DISABLE_AUTO_UPDATE=1
export SIMPLICIO_TOKIO_DAEMON=0   # 1 only for the daemon arm
export SIMPLICIO_JEV=on           # off only for the JEV-off arm
```

Record in the run log: model id and variant, binary `--version`, `git rev-parse HEAD` of the fixture, JEV and daemon values.

## Prompt A - arm M (Simplicio MCP, codegen)

```text
# BENCHMARK RUN - ARM M (Simplicio MCP + codegen)

You are executing a measured benchmark, not a demo. Follow the steps in order, record every number, stop at the stop condition. Never estimate a value you did not measure.

## Prepared by the operator
- repo: {{REPO}} - git initialized, `openapi.yaml` present (fixture {{FIXTURE}}), no generated code
- target: {{TARGET}} (react | csharp)
- binary: `simplicio` on PATH, SIMPLICIO_DISABLE_AUTO_UPDATE=1
- JEV: {{JEV}} - daemon: {{DAEMON}}
- tool policy: `simplicio_context` / `simplicio_file` to read, `simplicio_edit` to write, `simplicio_exec kind=argv` to run, `simplicio_codegen` to generate. No native read/write/edit/shell/glob.

## Phase 0 - shape (once, before touching the repo)
`simplicio shape "crie o app a partir de openapi.yaml e depois adicione o campo stock em Product" --json --repo .`
Record `shape`, `source`, `gate`, `confidence`, `elapsed_ms`.
Do not run `map`: with a contract in the repo the contract is the orientation.

## Phase 1 - creation
One command, timed:
- react:  `simplicio codegen generate --schema openapi.yaml --mode work-with --lang react --repo .`
- csharp: `simplicio codegen generate --schema openapi.yaml --preset dotnet-minimal --repo .`
Record: wall ms, exit, files created, bytes, first 6 paths.
Exit != 0: record it and STOP. Do not hand-write what the generator failed to produce.

## Phase 2 - edition A (field)
Edit `openapi.yaml`: add `stock` (integer, minimum 0) to `Product.properties`.
Apply:
- csharp: `simplicio codegen sync --repo . --check true`, then `simplicio codegen sync --repo .`
- react:  `simplicio codegen generate --schema openapi.yaml --mode work-with --lang react --repo .`
Record: check ms + exit (1 = drift detected), apply ms + exit, files changed, bytes changed.
Snapshot `src/App.impl.tsx` sha256 before and after (react): it must be identical.

## Phase 3 - edition B (entity + route)
Edit `openapi.yaml`: add schema `Supplier` (`id` uuid, `name` string, `lead_time_days` integer) and `GET /suppliers` returning `Supplier[]` (`operationId: listSuppliers`).
Apply exactly as phase 2. Same fields, same digest check.

## Phase 4 - verify
- csharp: `simplicio codegen sync --repo . --check true` must exit 0 (no drift left).
- react: run the generator once more. Count the files it changes; record the count even if it is not 0, and record whether `App.impl.tsx` stayed byte-identical.
Record one pass/fail per check.

## Output - exactly this, then STOP
One fenced json block:
{ "arm": "M", "target": "...", "fixture": "...", "model": "...", "jev": "...", "daemon": "...",
  "phase0": {"shape": "...", "source": "...", "gate": "...", "confidence": 0.0, "elapsed_ms": 0},
  "create": {"ms": 0, "exit": 0, "files": 0, "bytes": 0, "paths": []},
  "edition_field": {"check_ms": 0, "check_exit": 0, "apply_ms": 0, "apply_exit": 0, "files_changed": 0, "bytes_changed": 0, "seam_digest_stable": true},
  "edition_entity": {"check_ms": 0, "check_exit": 0, "apply_ms": 0, "apply_exit": 0, "files_changed": 0, "bytes_changed": 0, "seam_digest_stable": true},
  "verify": {"drift_clean": true, "idempotent_files": 0, "seam_digest_stable": true} }
Then one table row per phase: phase | wall_ms | exit | files | bytes.
Then stop. Do not open a PR, do not clean the repo, do not write more than the table.
```

## Prompt B - arm N (native tools, no Simplicio)

```text
# BENCHMARK RUN - ARM N (native tools, no Simplicio)

You are executing a measured benchmark. Same fixture, same model, same phases as arm M. Record every number; never estimate.

## Prepared by the operator
- repo: {{REPO}} - git initialized, `openapi.yaml` present (fixture {{FIXTURE}}), nothing else
- target: {{TARGET}} (react | csharp)
- tool policy: native read / write / edit / shell / glob only. Do not call any `simplicio_*` tool and do not run the `simplicio` binary.

## Phase 1 - creation
Write the {{TARGET}} app from `openapi.yaml` yourself. Feature parity with the generator is the bar:
- one list page and one create form per entity, routing between them;
- a typed API client function per operation;
- client-side validation for the create payload (required fields, minLength, enums);
- the implementation seam separated from the generated-looking parts (react: `src/App.impl.tsx`; csharp: `IApiService` implementation).
Record: wall ms to the moment the app builds, files written, bytes.

## Phase 2 - edition A (field)
Add `Product.stock` (integer, minimum 0) end to end: type, form field, validator, display.
Record wall ms, files changed, bytes changed, and the sha256 of the seam file before and after.

## Phase 3 - edition B (entity + route)
Add `Supplier` (`id` uuid, `name` string, `lead_time_days` integer) and `GET /suppliers` end to end: type, client function, list page, route.
Record the same fields.

## Phase 4 - verify
Run the project own checks: `npx tsc --noEmit` (react) or `dotnet build` (csharp). Record pass/fail and the error count.

## Output - exactly this, then STOP
Same JSON shape as arm M with `"arm": "N"`; `phase0` is null because this arm has no selector; `verify` reports `drift_clean: null` with the reason "no bindings in this arm".
Then the table, then stop.
```

## Prompt C - throughput (codegen, four cases, daemon off and on)

```text
# BENCHMARK RUN - THROUGHPUT

Run the creation and edition benchmark over the four cases, twice: daemon off, then daemon on. No model calls in either pass.

Cases: basic-react, basic-csharp, advanced-react, advanced-csharp.
Per case, in a fresh repo seeded with the fixture:
1. create (timed), record ms / exit / files / bytes;
2. edition A (field `stock`), record check ms+exit and apply ms+exit, files changed, bytes changed, seam digest;
3. edition B (`Supplier` + `GET /suppliers`), same fields;
4. verify: csharp drift check must exit 0 after the apply; react regenerate must change 0 files.

Then, once: `simplicio map --repo . --json` cold, again warm, `simplicio context --repo . --term Product --json`, and `simplicio benchmark mcp-cpu --json`.

For the sandbox pass, set HOME to the sandbox env home and run its own login first. Never copy `login.json` between homes: the refresh token rotates and the copy is rejected.

Output: one table per pass (case | create | check | apply | files | bytes | kept) plus the map/context/executor numbers, and the two raw JSONs.
```

## Prompt D - scorer

```text
# BENCHMARK SCORER

Inputs: the two arm JSONs (`{{RESULTS_MCP}}`, `{{RESULTS_NATIVE}}`) and the two session ids (`{{SESSION_MCP}}`, `{{SESSION_NATIVE}}`).

1. Equivalence gate FIRST. Same target, same fixture, same routes, same tests passing, comparable file sets (react: 16 or 27 generated files plus the seam; csharp: generated file plus bindings and receipt). If the artifacts differ, the run is INVALID - say so and stop.
2. Usage from the host database, never from the transcript:
   `select cost, tokens_input, tokens_output, tokens_reasoning, tokens_cache_read, tokens_cache_write from session_v2 where id = ?;`
3. Active wall = sum of assistant turn durations. Never cell wall: the arms run sequentially.
4. Split by phase using the JSON boundaries; report deltas, not cumulative totals.
5. Ratio = native / mcp. Above 1 means arm M is cheaper or faster.
6. Emit: one table per phase, one table for the session, at most 5 bullets of what it says, and the rule table (which shape goes to which path).
7. Publish `benchmarks/<date>-ab-<slug>.md` plus the two JSONs. A number you did not measure is `null` with the reason, never an estimate.
```

## Reading the result

| outcome | verdict |
|---|---|
| arm M faster and cheaper on creation AND edition | the surface pays for itself; default to it |
| arm M wins edition but loses creation | use it from the second turn on; native for the first pass |
| arm M loses both | the task is a 1-3 file edit with no contract: route it to `shape: native` |
| artifacts differ between arms | the run is invalid; fix the fixture or the parity bar before reporting ratios |

The measured baseline this prompt reproduces is in `2026-10-26-ab-create-edit.md` (3.42x cost and 4.70x wall for native over one session) and `2026-10-26-codegen-create-edit.md` (96-235 ms to create 16-27 files, 110-223 ms to regenerate 9-22).
