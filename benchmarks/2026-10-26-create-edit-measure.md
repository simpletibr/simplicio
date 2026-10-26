# Create / edit / measure: v3.9.2 vs v3.10.2 vs main, and where the time goes

Second half of the 2026-10-26 measurement. The version matrix answered "how fast is each surface"; this one runs the product loop the way a task actually uses it — **create** from a contract, **edit** the created tree, **measure** (bounded context) — on the same fixture, with a shell baseline for the same three phases.

Both reports come from the same harness: fresh `git init` copy per rep, resident daemon disabled (`SIMPLICIO_DAEMON_EXEC=0`, `SIMPLICIO_TOKIO_DAEMON=0`), auto-update disabled, no network, `/usr/bin/time -l` for wall and peak RSS.

## Results (median of 5 for create/edit, 3 for measure)

| phase | v3.9.2 | v3.10.2 | main | no-Simplicio (shell) |
|---|---|---|---|---|
| **create** — `codegen generate --lang rust` (1 OpenAPI → 2 files) | 0.06 s · 10.2 MB | **0.01 s** · 9.2 MB | **0.01 s** · 9.3 MB | 0.00 s · 1.9 MB (heredoc) |
| **edit** — one plan, 2 operations, 1 file | 2.79 s · 33.4 MB | **0.36 s** · 34.8 MB | **0.36 s** · 35.1 MB | 0.02 s · 14.4 MB (`python` replace) |
| **measure** — `context --term memory` | 0.09 s · 13,738 B | 0.28 s · 28,311 B | 0.26 s · 28,269 B | 0.09 s · **1,191,678 B** (`grep -rn` + `cat`) |

- **Create: 6x faster** (0.06 s → 0.01 s), same output (2 files).
- **Edit: 7.75x faster** (2.79 s → 0.36 s) at the same peak RSS. The edit result is byte-identical across versions (`A = "ONE"`, `B`, `C` inserted).
- **Measure: the payload is 42x smaller** than the raw shell answer (28,269 B vs 1,191,678 B), which is the token-economy claim with a number — but the newer versions return **2x more** than 3.9.2 and take **3x longer** (0.09 s → 0.26–0.28 s).
- The shell is faster on all three phases because it does none of the work: no contract parse, no receipt, no governed write, no bounded packet. That is the correct trade to state, not a competitor to beat.

## The whole product loop, in one number

For a task that creates, edits and then re-orients, the loop cost on `main` is **0.01 + 0.36 + 0.26 ≈ 0.63 s** of local tool time versus **≈ 5.0 s** on 3.9.2 (0.06 + 2.79 + 0.09 + the extra map/context work it needed). The 3.9.2 edit path is the single largest win in the whole comparison.

## Session analysis — what this run taught us

### What is already fast (keep)

| surface | measured | vs 3.9.2 |
|---|---|---|
| repository map | 0.34–0.37 s | **13.1x** |
| deterministic edit | 0.36 s | **7.75x** |
| CPU executor | 0.25–0.32 s | **8.5–10.9x** |
| codegen | 0.01 s | **6x** |
| benchmark suite | 0.42–0.46 s | **6.7x** |

### What is slow or blocking (fix in this order)

1. **Fast-path planning regressed.** `plan` went from 0.18 s (3.9.2) to 0.48 s (3.10.2) and 0.37 s (main), with an identical ~1.97 KB document. Every routed task pays it before any work starts. Target: back to ≤0.20 s. This is the highest-leverage fix for time-to-first-tool-call.
2. **Bounded context grew 2x and got 3x slower.** 13.7 KB → 28.3 KB and 0.09 s → 0.26–0.28 s. The payload is still 42x smaller than raw reads, but the regression costs tokens on every orientation. Target: a term budget that keeps the 3.9.2 payload while keeping the 3.10 ranking quality.
3. **Auth verification can lock the whole host.** During this session the local login's access token expired, every Simplicio MCP call returned "could not verify the subscription", and because the OpenCode enforcement plugin fails closed, native tools were blocked too: the agent had **zero** working tools until a human re-logged in. That cost roughly two hours of wall time. Fix: offline grace for a still-valid local session plus a clear re-login prompt instead of total lockout.
4. **27 flaky bin integration tests.** They pass one by one and fail under parallel load on an 8 GB host, so `scripts/verify.sh` and the pre-push hook need `--no-verify` on nearly every push. Fix: pin them to a serial group or make them resource-aware; the local gate must be trustworthy without a bypass.
5. **JEV cannot be measured yet.** `opencode` (`jev-1.13`) needs `OPENCODE_API_KEY` (absent); `opencode-free` returned `JEV_RATE_LIMITED` after one 0.74 s call; and the classifier is not in the routing path (`plan` has no JEV field). To include it: set a key, install the plugin, measure p50/p95 and agreement against the deterministic router, and only then wire it as the last hop.
6. **Build time is still the long pole for development.** Cold `cargo check -p simplicio-codegen --tests -j 3` is 99.94 s on an idle machine (it was 255 s under load). 16 `main_parts` chunks remain (68,226 lines). Each extraction is mechanical and ratchets the architecture gate down.
7. **Pre-push friction.** `simplicio dod orphans` runs without `--confirm` in `mode=auto` and blocks every push until each step is repeated by hand. The read-only gates should confirm themselves (done for `dod-gate.sh` and `hooks/action_gate.py` in #7812, but any new caller repeats the trap).

### Expected effect on execution time

| fix | measured today | target | effect |
|---|---|---|---|
| plan regression | 0.37–0.48 s | ≤0.20 s | −0.2 s per routed task, before the first tool call |
| context payload | 28.3 KB | ~14 KB | halves orientation tokens on every turn |
| auth lockout | 2 h lost | 0 | removes the worst wall-clock failure of the session |
| flaky bin tests | `--no-verify` on every push | green gate | removes a manual step per PR |
| chunk migration | 68,226 lines left | 0 | cold check 99.94 s → target <60 s |

### What is left to conclude

- `#7750` (16 chunks), `#7628` AC3 (needs JDK + npm packages), `#7582` (SQL Server needs docker), `#7590`/`#7572` (production Ed25519 key + deploy), `#7589` (tracking), `#7754` (owner session).
- JEV: key + plugin install, then the classifier lane report.
- The plan and context regressions above are not yet filed as issues; they are the next two.

## Reproduce

```bash
cp -R fixture-base work && (cd work && git init -q && git add -A && git commit -qm seed)
SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 /usr/bin/time -l ./simplicio-main codegen generate --schema api.json --lang rust --repo work
SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 /usr/bin/time -l ./simplicio-main edit '<plan.json>' --repo work --json
SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 /usr/bin/time -l ./simplicio-main context --repo work --term memory --json
```
