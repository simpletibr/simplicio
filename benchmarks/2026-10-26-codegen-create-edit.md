# Codegen is the fastest creation and edition path (measured 2026-10-26)

The claim under test: for programming work, generating and regenerating from a contract beats the model editing files one by one — in wall time, in tokens and in how many files land at once.

Measured on one Mac (8 CPUs, release build, no daemon unless stated), two fixtures, two targets:

- **basic**: 2 entities, 2 routes, no enums/refs (`openapi-small.yaml`).
- **advanced**: 13 schemas, 8 routes, enums, `$ref` cycles, paging, pages ( `openapi-advanced.yaml`).
- **React**: `codegen generate --mode work-with --lang react` (Vite + React 19 admin app per entity).
- **C#**: `codegen generate --preset dotnet-minimal`.

Every number is one measured command (JSON in `2026-10-26-codegen-bench.json`).

## Creation

| case | wall | files written | bytes |
|---|---|---|---|
| basic, React | **234.5 ms** | 16 | 23,361 |
| basic, C# | **117.4 ms** | 2 | 2,768 |
| advanced, React | **96.4 ms** | 27 | 59,829 |
| advanced, C# | **113.1 ms** | 2 | 8,829 |

Zero model tokens, zero network: the whole app (pages, typed client, validators, routing) comes from the contract.

## Edition (change the contract, regenerate everything)

Two editions per case: **E1** add a field to `Product`, **E2** add a new entity `Supplier` plus its route.

| case | edition | path | drift check | apply | files changed | bytes |
|---|---|---|---|---|---|---|
| basic, React | add field | `generate` again | — (no bindings) | **115.1 ms** | 9 | 22,113 |
| basic, React | add entity | `generate` again | — | **110.4 ms** | 11 | 28,032 |
| advanced, React | add field | `generate` again | — | **222.7 ms** | 20 | 58,104 |
| advanced, React | add entity | `generate` again | — | **128.4 ms** | 22 | 64,023 |
| basic, C# | add field | `sync` | 200.7 ms (exit 1 = drift) | **114.5 ms** | 3 | 3,543 |
| basic, C# | add entity | `sync` | 272.2 ms (exit 1) | **125.4 ms** | 3 | 4,069 |
| advanced, C# | add field | `sync` | 264.9 ms (exit 1) | **126.8 ms** | 3 | 9,604 |
| advanced, C# | add entity | `sync` | 186.7 ms (exit 1) | **157.3 ms** | 3 | 10,130 |

The C# rows also write `.simplicio/codegen/bindings.json` and a `sync-receipt.json` — the governed receipt that makes drift detectable before a commit.

For the React work-with app, the hand-written `src/App.impl.tsx` is **byte-identical after every regeneration** (checked by digest), which is what makes "rerun the generator" safe: generated files are rewritten, your implementation file is not.

### What that replaces

The same shape of edit measured with the model editing files by hand (two-file edition, same host, 2026-10-26 in-session A/B):

| path | wall (active) | input tokens | output tokens | cost |
|---|---|---|---|---|
| native (model edits 2 files) | **13.19 s** | 1,973 | 861 | $0.001245 |
| codegen (regenerates 9-22 files) | **110-223 ms** | 0 | 0 | $0 |

**~60-120x faster and zero tokens**, and the change lands in 9-22 files at once instead of one model turn per file.

## Map reuse

One cold map per repository generation, then reuse:

| step | wall | note |
|---|---|---|
| `map` cold | **213-376 ms** | writes a 4.8-5.7 KB `project-map.json` |
| `map` warm (same generation) | **178-249 ms** | cache hit, no rebuild |
| `context --term Product` | **196 ms** | 74 ms with the resident daemon |

The trap: mapping again inside the same generation pays 0.2-0.4 s for nothing. Map once, then ask `context` for the bounded slice. **For a codegen task, skip the map entirely** — the contract is the orientation, and every number in the creation table above ran without one.

## Daemon and CPU executor

Interleaved A/B, 3 rounds, same fixture (advanced React):

| step | daemon off | daemon on |
|---|---|---|
| generate | 207.1 ms | 195.9 ms |
| map cold | 213.0 ms | 286.4 ms |
| map warm | 177.5 ms | 210.5 ms |
| `context --term` | 195.4 ms | **74.1 ms** |
| regenerate | 258.5 ms | 262.8 ms |
| `shape` | 165.6 ms | 177.5 ms |
| **total** | **1,217 ms** | **1,207 ms** (-0.8%) |

Daemon start costs 341-458 ms. The resident daemon does not speed up codegen (it is in-process Rust either way); it makes repeated **context** reads 2.6x faster. `simplicio benchmark mcp-cpu` (the executor path): cold single call p50 **113.6 ms**, and with 5 resident slots p50 **343 us** at **6,142 calls/s** — that is the difference between spawning a process per call and keeping the executor warm.

Rule: one-shot CLI batch -> daemon off; an agent making many context/tool calls -> daemon on.


## Sandbox confirmation (3.10.3, isolated HOME)

The same benchmark re-run against the **shipped 3.10.3 binary** inside the sandbox environment (sandbox-simplicio-mcp/envs/3.10.3, its own HOME, its own device login - no credential copied between homes), once with the resident daemon off and once on.

| case | create (daemon off) | field edition | entity edition | create (daemon on) | field | entity |
|---|---|---|---|---|---|---|
| basic-react | **198.8 ms** | 111.7 ms | 190.5 ms | **119.0 ms** | 181.6 ms | 120.5 ms |
| basic-csharp | **125.6 ms** | 200.3 ms | 130.1 ms | **130.3 ms** | 116.1 ms | 177.4 ms |
| advanced-react | **221.9 ms** | 185.0 ms | 105.3 ms | **118.8 ms** | 124.1 ms | 111.5 ms |
| advanced-csharp | **153.7 ms** | 235.9 ms | 106.3 ms | **139.2 ms** | 119.3 ms | 192.7 ms |

Files landing and the hand-written seam match the source-build run: 16-27 files created, 9-22 regenerated, the React implementation file byte-identical (kept per case: basic-react=True, basic-csharp=False, advanced-react=True, advanced-csharp=False).

Map reuse in the sandbox: cold **361.2 / 299.8 ms**, warm **198.5 / 214.0 ms**, context --term **239.9 ms** with the daemon off and **100.6 ms** on - the same 2.4x context win, same 5,693-byte map.

JEV inside the same sandbox: plugin installed into that HOME, backend typesafe, key at 0600. A task the rules cannot decide, "resuma o README", returned source=jev, gate=accepted, p=0.84 in **518 ms**; a rules-decided task stayed deterministic in **25 ms** with no network.

## Reproduce

```bash
# creation
simplicio codegen generate --schema openapi.yaml --mode work-with --lang react --repo .
simplicio codegen generate --schema openapi.yaml --preset dotnet-minimal --repo .

# edition (C#: bound output)
simplicio codegen sync --repo . --check true   # exit 1 while stale
simplicio codegen sync --repo .

# edition (React work-with: not bound yet, regenerate)
simplicio codegen generate --schema openapi.yaml --mode work-with --lang react --repo .

# map reuse
simplicio map --repo . --json
simplicio context --repo . --term Product --json
```

## Gaps this measurement exposed

1. **`--mode work-with` writes no codegen bindings.** `sync --check` therefore cannot gate a React work-with app; today the edition path is "run the generator again" (safe because `App.impl.tsx` is preserved, but there is no drift receipt). Binding those outputs is the next fix.
2. **C# preset + sync works**, including drift detection, but only via the binding path (`sync`); passing `--schema` + `--preset` to `sync` fails with `preset_contract_unparseable`, which the binding path hides.
3. **Map is not needed for codegen** and should not be in the flow when a contract exists; the 0.2-0.4 s it costs buys nothing there.
