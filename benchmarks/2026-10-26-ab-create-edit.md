# A/B with and without the MCP: creation, then edition (2026-10-26)

The question: for a small programming task, does the MCP surface pay for itself across the two phases the product actually uses — **creation** and then **edition** — or does the native baseline win?

## Method

Two identical arms, each its own git repository seeded with the same `README.md` and `TASK.md`, same model (`deepseek-v4.1-flash`, `opencode-go`, variant high), same host, sequential.

- **Phase 1, creation**: create `calc/ops.py` with `add`/`sub`/`mul` and `calc/test_ops.py` with 3 pytest cases; finish at `3 passed`.
- **Phase 2, edition**: in the same repository, add `div(a, b)` raising `ValueError("division by zero")`, export it, add exactly 2 tests, keep the existing 3; finish at `5 passed`.

- Arm M: only `simplicio_context`/`simplicio_file` to read, `simplicio_edit` to write, `simplicio_exec kind=argv` to run.
- Arm N: only native `read`/`write`/`edit`/`shell`/`glob`.

Usage is provider-billed, read from OpenCode's `session_v2` (`cost`, `tokens_*`) per phase; wall time is `time_updated - time_created`.

## Results

### Phase 1 — creation

| metric | MCP | native | ratio |
|---|---|---|---|
| cost (USD) | 0.006307 | **0.001438** | 4.39x |
| wall | 36.73 s | **9.17 s** | 4.01x |
| input tokens | 27,076 | **5,290** | 5.12x |
| output tokens | 1,610 | **690** | 2.33x |
| reasoning tokens | 1,124 | **7** | 160x |
| cache-read tokens | 201,728 | 75,520 | 2.67x |
| messages | 12 | **7** | 1.71x |
| tool calls | 9 | **5** | 1.80x |

### Phase 2 — edition

| metric | MCP | native | ratio |
|---|---|---|---|
| cost (USD) | 0.002984 | **0.002003** | 1.49x |
| wall | 40.37 s | **30.15 s** | 1.34x |
| input tokens | 11,953 | **3,247** | 3.68x |
| output tokens | **1,071** | 1,285 | 0.83x |
| reasoning tokens | **278** | 322 | 0.86x |
| cache-read tokens | **127,104** | 183,936 | 0.69x |
| messages | **8** | 13 | 0.62x |
| tool calls | **5** | 6 | 0.83x |

### Both phases

| metric | MCP | native | ratio |
|---|---|---|---|
| cost | 0.009291 | **0.003441** | **2.70x** |
| wall | 77.10 s | **39.32 s** | **1.96x** |

Both arms produced byte-equivalent outcomes at each phase (3 passed, then 5 passed, same files).

## What it says

- **Creation is where the MCP costs most**: 4.4x the money and 4.0x the wall time, dominated by orientation and the per-call envelope for a three-file module. Reasoning tokens (1,124 vs 7) show the model searching for a path the native arm already knew.
- **Edition narrows the gap**: 1.49x cost and 1.34x wall. The MCP arm used fewer messages and tool calls, and it read less cache, because the second phase reuses the shape of the first.
- **Neither phase beats the native baseline.** For a small, greenfield, well-known task, the cheapest correct path is the native one.

## Rule for the flow

| situation | path | why |
|---|---|---|
| create/edition of 1-3 files in a known layout | **native** | measured 2.7x cheaper over the two phases |
| unfamiliar tree, >10 files, or a contract to derive | **MCP** (map/context/codegen) | native would scan the tree and dump raw files |
| anything that needs governed writes, receipts or a drift gate | **MCP** | the native path cannot produce them |
| repeated turns on the same repository | **MCP** | the prefix is cached and orientation is reused |

The MCP is a governance and navigation layer, not a speed layer for small edits. The product flow must choose by task shape, not by ideology.

## Reproduce

Four sessions on the same host, same model, same seeded repositories; the usage JSON is in this folder as `../2026-10-26-ab2-usage.json`.
