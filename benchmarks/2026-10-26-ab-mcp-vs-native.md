# A/B: Simplicio MCP vs native tools — greenfield micro-task (2026-10-26)

Two agent sessions did the **same task on two identical, freshly seeded git repos**, one using only Simplicio MCP tools and one using only native host tools. Provider-reported usage, wall time and resident memory were recorded; the artifacts produced were compared at the end.

This is a **micro-task** measurement: it answers "what does the MCP cost when the repository is trivial?", not "does bounded context save tokens on a real codebase?". The second question needs a navigation task and is listed under Scope.

## Method

- Host: same machine, same OpenCode host, same model `deepseek-v4.1-flash` (provider `opencode-go`, variant `high`) for both arms.
- Seeds: `bench-ab/arm-mcp` and `bench-ab/arm-native`, each `git init`-ed with the same three files (`README.md`, `slug/__init__.py`, `slug/test_slugify.py` with five tests) and the same `TASK.md`.
- Task, pinned so both arms converge: implement `slugify` and `truncate_slug` in `slug/slugify.py`, export both, keep the five existing tests unchanged, add exactly two named tests, and finish when `python3 -m pytest slug -q` reports `7 passed`.
- Arm A: only `simplicio_context`/`simplicio_map` to read, `simplicio_edit` to write, `simplicio_exec` (kind=argv) to run commands.
- Arm B: only native `read`, `write`, `edit`, `shell`.
- Both arms ran sequentially, one subagent session each, with the same host configuration and the same tool catalogue visible to the model. The only difference was the tool instruction.
- Metrics come from OpenCode's local database (`session_v2.cost`, `tokens_input`, `tokens_output`, `tokens_reasoning`, `tokens_cache_read`, `tokens_cache_write`) — provider usage as billed, not estimated from bytes.

A first exploratory run was discarded: the two arms produced different artifacts (7 vs 10 tests), so the task was pinned and both arms re-run.

## Results

| Metric | With Simplicio MCP | Native tools | Ratio |
|---|---|---|---|
| Outcome | 7 passed, same 3 files | 7 passed, same 3 files | equal |
| Wall time | **99.01 s** | **23.69 s** | 4.18× slower |
| Assistant messages | 22 | 10 | 2.2× |
| Tool calls | 19 | 8 | 2.4× |
| Input tokens | **15,875** | **2,930** | 5.42× |
| Output tokens | **3,788** | **973** | 3.89× |
| Reasoning tokens | **2,840** | **553** | 5.14× |
| Cache-read tokens | 470,528 | 135,296 | 3.48× |
| Cache-write tokens | 0 | 0 | — |
| **Total cost (USD)** | **$0.007769634** | **$0.001760988** | **4.41×** |
| Resident RAM (peak, MCP server) | 328.6 MB | 0 MB (no daemon) | — |
| MCP server CPU time (cumulative) | 13.58 s | 0 s | — |

Native tool mix: `read` 3, `shell` 2, `write` 2, `edit` 1. MCP arm: 19 calls through the host's generic `execute` wrapper (each `simplicio_*` call is one wrapper execution, so the wrapper is what the host counts).

## What the numbers say

- On a three-file greenfield task the MCP arm cost **4.4×** more and took **4.2×** longer.
- The cost is dominated by **orientation and payload shape**, not by the runtime being slow: `simplicio_context` returns a bounded packet for a repository with three files — there is nothing to bound, so the packet is pure overhead — and each `simplicio_edit` carries a JSON operations envelope, while a native `write` is one call with the file body.
- The MCP arm also needs more turns (19 vs 8), and every turn re-reads the growing context (cache-read 470k vs 135k).
- Resident cost is real and asymmetric: the MCP adds a `serve --mcp --stdio` process that peaked at **328.6 MB RSS** and 13.58 s of CPU; the native arm adds no process.

## Scope (read before citing)

- This does **not** contradict the bounded-context claim measured elsewhere on a real codebase (AST-safe bug fix inside a large repository). That case pays for navigation: many files, many greps, many raw dumps. Here there was nothing to navigate.
- A greenfield micro-task is the worst case for the MCP: orientation has zero information to compress and the edit envelope has no siblings to reconcile.
- The right follow-up is the same protocol on a repo-navigation task (locate + fix a bug in a 1k+ file tree) and on a multi-file refactor, where bounded context should win. Until those numbers exist, no savings claim should be made for micro-tasks.
- No provider cache hit is claimed beyond the `tokens_cache_read` the provider reported.

## Raw data

```json
{
  "mcp": {"session": "ses_e89c0353dffe78iEobKgG9v7vq", "model": {"id": "deepseek-v4.1-flash", "providerID": "opencode-go", "variant": "high"},
          "cost_usd": 0.007769634, "tokens_input": 15875, "tokens_output": 3788, "tokens_reasoning": 2840,
          "tokens_cache_read": 470528, "tokens_cache_write": 0, "wall_s": 99.01, "messages": 22, "tool_calls": 19,
          "resident_peak_rss_mb": 328.6, "server_cpu_time_s": 13.58},
  "native": {"session": "ses_e89bea0faffeYfDGnqRrMr50w4", "model": {"id": "deepseek-v4.1-flash", "providerID": "opencode-go", "variant": "high"},
          "cost_usd": 0.001760988, "tokens_input": 2930, "tokens_output": 973, "tokens_reasoning": 553,
          "tokens_cache_read": 135296, "tokens_cache_write": 0, "wall_s": 23.69, "messages": 10, "tool_calls": 8,
          "resident_peak_rss_mb": 0, "server_cpu_time_s": 0}
}
```

## Reproduce

1. Seed two identical repos (three files, five tests, `git init`).
2. Give both sessions the same `TASK.md` and the same model; restrict one to `simplicio_*` and the other to native tools.
3. Read `session_v2` for `cost` and `tokens_*`; sample the `serve --mcp --stdio` process for RSS/CPU during the MCP arm.
