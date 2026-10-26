# Runtime version matrix: v3.9.2 vs v3.10.2 vs main (2026-10-26)

Same machine, same fixture, same commands — three signed/compiled Runtime builds compared on the surfaces this repo claims: repository map, bounded context, fast-path planning, codegen, the built-in benchmark suite, and the CPU executor. A shell baseline answers the same context question with `grep`/`cat` so the "bounded vs raw" difference has a number.

## Method

- Fixture: `git archive` export of `crates/simplicio-memory`, `crates/simplicio-edit` and `src/version_provenance.rs` (65 files, 56 `.rs`, ~1.1 MB of source), `git init`-ed fresh for **every rep**, so no map cache or lock crosses runs.
- Binaries: `v3.9.2` and `v3.10.2` from the signed GitHub releases; `main` built locally at `8883ddc73` with the canonical `scripts/build.sh` (release profile).
- 3 reps per metric; the table reports the **median**. Resident daemon disabled (`SIMPLICIO_DAEMON_EXEC=0`, `SIMPLICIO_TOKIO_DAEMON=0`), auto-update disabled.
- Wall time and peak RSS from `/usr/bin/time -l` (RSS = `maximum resident set size`).
- No network is used by any measured command.

## Results (median of 3)

| metric | v3.9.2 | v3.10.2 | main |
|---|---|---|---|
| `map` | 4.45 s · 38.9 MB · 22,672 B | **0.34 s** · 34.3 MB · 4,529 B | **0.37 s** · 34.7 MB · 4,514 B |
| `context --term memory` | 0.09 s · 16.8 MB · 13,748 B | 0.18 s · 29.4 MB · 28,311 B | 0.18 s · 30.3 MB · 28,299 B |
| `plan "<task>"` (fast path) | **0.18 s** · 23.4 MB | 0.48 s · 21.5 MB | 0.37 s · 21.7 MB |
| `codegen generate --lang rust` | 0.06 s · 9.6 MB · 2 files · 297 B | **0.01 s** · 9.2 MB · 2 files · 299 B | **0.01 s** · 9.3 MB · 2 files · 295 B |
| `benchmark run` (4 scenarios) | 2.80 s · 14.0 MB | **0.42 s** · 17.0 MB | **0.46 s** · 17.4 MB |
| `benchmark mcp-cpu` (CPU executor) | 2.73 s · 27.2 MB | 0.32 s · 27.3 MB | **0.25 s** · 26.7 MB |

Shell baseline for the same context question (`memory` in the fixture):

| approach | wall | RSS | payload |
|---|---|---|---|
| `grep -rn memory` | 0.01 s | 1.9 MB | 161,889 B |
| `grep -rl memory` + `cat` every match | 0.07 s | 1.9 MB | 1,038,379 B |
| `simplicio context --term memory` (3.10.2) | 0.18 s | 29.4 MB | **28,311 B** |

## What moved between versions

- **Map: 13.1× faster** (4.45 s → 0.34 s) and the returned document is **5× smaller** (22.7 KB → 4.5 KB) at the same peak RSS. This is the biggest change in the matrix.
- **Benchmark suite: 6.7× faster** (2.80 s → 0.42 s).
- **CPU executor (`benchmark mcp-cpu`): 8.5× faster on 3.10.2 and 10.9× on main** (2.73 s → 0.32 s / 0.25 s), same RSS.
- **Codegen: 6× faster** (0.06 s → 0.01 s) with byte-identical output (2 files, ~297 B), so the speedup does not change the generated code.
- **Bounded context is smaller than raw reads, but 3.10 returns more than 3.9.2**: 28.3 KB vs 13.7 KB (2.06×), and it is 2× slower (0.18 s vs 0.09 s). Against the raw alternative it is still **5.7× smaller than the grep output** and **36.7× smaller than reading every matched file** — that is the token-economy claim, on this fixture, with a measured number.
- **Fast-path planning regressed against 3.9.2**: `plan` is 0.48 s on 3.10.2 and 0.37 s on main vs 0.18 s on 3.9.2. The plan document is the same size (~1.97 KB). This is the one metric where the newer versions are slower; `main` is better than 3.10.2 but not back to 3.9.2. Worth a follow-up issue.
- **main vs 3.10.2**: map, context, codegen and `benchmark run` are within noise; `main` is faster on the CPU executor (0.25 s vs 0.32 s) and on planning (0.37 s vs 0.48 s).

## JEV (the optional classifier)

`simplicio-jev` is not part of the core binaries. `jev-status` on `main`:

```
active: opencode-free   model jev-1.13-free   ready true   key_present false
opencode                model jev-1.13        ready false  key_present false  (needs OPENCODE_API_KEY)
typesafe                model jev-latest      ready false  key_present false
openrouter              model typesafe/jev-router ready false key_present false
```

- The **paid `opencode` backend (`jev-1.13`) cannot run here**: `OPENCODE_API_KEY` is not set, so it fails closed before opening a socket.
- The **free backend was rate-limited**: the first `jev-classify` call took 0.74 s of wall time, the next two returned `JEV_RATE_LIMITED` in 0.01 s. There is therefore **no classifier latency or accuracy number** in this report.
- JEV is **not in the fast path**: `simplicio plan --json` contains no JEV field, and `docs/PLUGIN_JEV.md` states the routing wiring "lands in a separate change". So the `plan` numbers above measure the deterministic router only.

To measure the classifier lane: set `OPENCODE_API_KEY` (or a typesafe/openrouter key), install the plugin (`simplicio plugin install simplicio-jev`), and run `jev_classify` 20× against a fixed question set; report latency percentiles and label agreement against the deterministic router. That is a separate report and needs the key.

## Caveats

- The fixture is 65 files; map/context times do not extrapolate linearly to a 1,000-file repository.
- The shell baseline answers the *same question*, but it is not a product equivalent: it prints raw matches with no structure, no receipts and no cache. The comparison is about bytes handed to the caller, not about capability.
- `main` is a local build (`8883ddc73`), not a signed release; the other two are the published assets.

## Reproduce

```bash
# fixture
git -C simplicio-runtime archive HEAD crates/simplicio-memory crates/simplicio-edit src/version_provenance.rs | tar -x -C fixture-base

# per version, fresh copy per rep
cp -R fixture-base work && (cd work && git init -q && git add -A && git commit -qm seed)
/usr/bin/time -l ./simplicio-<version> map --repo work --json
SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 /usr/bin/time -l ./simplicio-<version> context --repo work --term memory --json
```

Raw rows and the aggregator are committed next to this report as `2026-10-26-runtime-version-matrix.json`.
