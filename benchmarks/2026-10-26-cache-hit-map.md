# Cache hit with `simplicio_map`: higher ratio, higher cost (2026-10-26)

The question: does orienting with `simplicio_map` raise the LLM's prompt-cache hit rate enough to pay for itself?

Two sessions, same model, same repository, same one-file read task ("list the 5 embedding-related functions in `vector_memory.rs` with file:line"). Both used the same MCP tool surface; the only difference is the method.

- **with map**: `simplicio_map` -> `simplicio_context` -> answer.
- **no map**: `simplicio_file` grep/read only, no map, no context.

Usage comes from OpenCode's local `session_v2` (`cost`, `tokens_*`) - provider-billed numbers.

## Result

| metric | with `simplicio_map` | without map | delta |
|---|---|---|---|
| **cache hit ratio** (cache_read / (cache_read + input)) | **88.75 %** | 76.64 % | **+12.1 pts** |
| cache-read tokens | 207,744 | 85,760 | 2.42x |
| input tokens | 26,327 | 26,142 | +0.7 % |
| output tokens | 1,491 | 805 | 1.85x |
| reasoning tokens | 1,149 | 205 | 5.6x |
| **total cost (USD)** | **0.006156** | **0.004785** | **+28.7 %** |
| wall time | 31.46 s | 14.92 s | 2.11x |
| assistant messages | 12 | 7 | 1.71x |
| tool calls | 9 | 4 | 2.25x |

Both arms answered correctly with real `file:line` citations.

## What it means

- **The map does raise the cache hit rate** - 88.8 % vs 76.6 %. The map packet is large, stable and reused, so more of the prompt prefix is served from cache.
- **But the ratio is not the goal.** The map arm read **2.4x more cached tokens**, took **2.1x longer** and cost **28.7 % more**, because it spent four extra turns and produced a bigger packet for a one-file question.
- **Cache-hit percentage alone is a misleading metric**: a higher ratio on a larger prompt can still cost more. Optimise for total cost and wall time, and read the ratio only as a diagnostic.
- **The map pays when the alternative is scanning.** On the version matrix, the same map replaces a 1.19 MB `grep` + `cat` answer with a 28 KB packet. On a single known file it does not: the file is cheaper to read directly.

## Rule for the fast path

| situation | method |
|---|---|
| one file, you know the name | `simplicio_file read` (or native read) - **no map** |
| unknown tree, or >10 files | `simplicio_map` -> `simplicio_context --term` |
| second and later turns on the same repository | reuse the map; the prefix is already cached |

## Tooling finding (host usability)

A subagent of type `explore` receives **no Simplicio MCP tools** and native tools are blocked by the enforcement plugin, so it cannot read anything at all. `general` subagents get the MCP surface and work. Until `explore` gets the MCP tools (or an exemption), it is unusable on this host; that is a concrete "can the LLM use our tools" failure, not a model failure.

## Reproduce

```sql
select cost, tokens_input, tokens_output, tokens_reasoning,
       tokens_cache_read, tokens_cache_write
from session_v2 where id in ('ses_e89454f48ffeKgceX8YA1bCfaK', 'ses_e89454f47ffeOqkt78vaHCOwoM');
```

Sessions: `ses_e89454f48ffeKgceX8YA1bCfaK` (with map), `ses_e89454f47ffeOqkt78vaHCOwoM` (without).
