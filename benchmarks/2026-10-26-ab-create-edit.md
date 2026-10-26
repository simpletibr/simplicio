# A/B with and without the MCP: one session, creation then edition (2026-10-26)

The question: for a small programming task that spans **creation and then edition**, does the MCP surface pay for itself, or does the native baseline win?

## Design correction

An earlier run used four sessions (two arms x two phases). That measures two separate agents, not the workflow a user actually has: the same agent creates the module and then edits it. This run uses **two sessions**, one per arm, and each session performs creation and then edition. The edition delta is the session state after phase 2 minus the snapshot taken between the phases, so each phase is billed to the session that owns it.

## Method

Two identical arms, each its own git repository seeded with the same README.md and TASK.md, same model (deepseek-v4.1-flash, opencode-go, variant high), same host, sequential, same session per arm.

- **Phase 1, creation**: create calc/ops.py with add/sub/mul and calc/test_ops.py with 3 pytest cases; finish at 3 passed.
- **Phase 2, edition**: in the same session and the same repository, add div(a, b) raising ValueError("division by zero"), export it, add exactly 2 tests, keep the existing 3; finish at 5 passed.
- Arm M: only simplicio_context / simplicio_file to read, simplicio_edit to write, simplicio_exec kind=argv to run.
- Arm N: only native read / write / edit / shell / glob.

Usage is provider-billed, read from OpenCode's session_v2 (cost, tokens_*). Wall time is computed from the message rows: **active** is the sum of each assistant turn's duration, which removes the idle gap between the phases (the arms ran sequentially, so the cell wall of the second arm included waiting for the first).

## Results

### Phase 1 - creation

| metric | MCP | native | ratio |
|---|---|---|---|
| cost (USD) | 0.004773 | **0.000800** | 5.97x |
| active wall | 67.97 s | **8.41 s** | 8.08x |
| input tokens | 14,003 | **1,323** | 10.58x |
| output tokens | 1,915 | **508** | 3.77x |
| reasoning tokens | 1,219 | **99** | 12.31x |
| cache-read tokens | 264,064 | **79,104** | 3.34x |
| turns | 12 | **5** | 2.40x |
| tool calls | 9 | **5** | 1.80x |

### Phase 2 - edition (same session, delta from the phase-1 snapshot)

| metric | MCP | native | ratio |
|---|---|---|---|
| cost (USD) | 0.002225 | **0.001245** | 1.79x |
| active wall | 33.55 s | **13.19 s** | 2.54x |
| input tokens | 3,006 | 1,973 | 1.52x |
| output tokens | 1,060 | **861** | 1.23x |
| reasoning tokens | 1,003 | **34** | 29.5x |
| cache-read tokens | 178,688 | **137,472** | 1.30x |
| turns | **6** | 8 | 0.75x |
| tool calls | **7** | 9 | 0.78x |

### Whole session (creation + edition)

| metric | MCP | native | ratio |
|---|---|---|---|
| cost (USD) | 0.006998 | **0.002045** | **3.42x** |
| active wall | 101.52 s | **21.60 s** | **4.70x** |
| input tokens | 17,009 | **3,296** | 5.16x |
| output tokens | 2,975 | **1,369** | 2.17x |
| reasoning tokens | 2,222 | **133** | 16.7x |
| cache-read tokens | 442,752 | **216,576** | 2.04x |

Both arms produced equivalent artifacts at each phase (3 passed, then 5 passed, same files, same exports).

## What it says

- **Creation dominates the bill.** 5.97x the money and 8.08x the active wall for a three-file module. The reasoning column is the tell: 1,219 vs 99 tokens, i.e. the MCP arm spent its budget deciding *how* to use the surface rather than writing the code.
- **Edition narrows but does not close the gap.** 1.79x cost, 2.54x active wall. The MCP arm used fewer turns and fewer tool calls (6/7 vs 8/9) and read less cache, because phase 2 reused the shape of phase 1, but each call still carries the envelope.
- **In-session reuse helps the MCP more than it helps native** (creation 8.08x -> edition 2.54x), which is exactly why the MCP belongs in repeated turns on the same repository.
- **Native still wins the small greenfield task end to end**: 3.42x cheaper and 4.70x faster over one session.

## Rule for the flow

| situation | path | why |
|---|---|---|
| create or edit 1-3 files in a known layout, one session | **native** | measured 3.42x cheaper, 4.70x faster over creation + edition |
| unfamiliar tree, >10 files, or a contract to derive | **MCP** (map/context/codegen) | native would scan the tree and dump raw files |
| governed write, receipt, drift gate, audit trail | **MCP** | the native path cannot produce them |
| repeated turns on the same repository | **MCP** | cached prefix and reused orientation: the edition gap is 3.2x smaller than the creation gap |

The MCP is a governance and navigation layer, not a speed layer for small edits. The flow chooses by task shape.

## Reproduce

Two sessions on one host, same model, same seeded repositories. Raw metrics: 2026-10-26-ab3-usage.json (per phase, including active wall and tool-call mix).
