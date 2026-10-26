# Harness for the 2026-10-26 measurements

The three reports published on 2026-10-26 were produced with these scripts:

- [`../2026-10-26-runtime-version-matrix.md`](../2026-10-26-runtime-version-matrix.md) — map, context, plan, codegen, benchmark suite, CPU executor across v3.9.2 / v3.10.2 / main.
- [`../2026-10-26-create-edit-measure.md`](../2026-10-26-create-edit-measure.md) — create / edit / measure loop plus the session analysis.
- [`../2026-10-26-ab-mcp-vs-native.md`](../2026-10-26-ab-mcp-vs-native.md) — agent A/B, measured from OpenCode's local `session_v2` (`cost`, `tokens_*`).

Raw rows are in `data/`; the numbers in the reports come from those files.

## Rebuild the fixture

```bash
mkdir fixture-base
git -C /path/to/simplicio-runtime archive HEAD \
  crates/simplicio-memory crates/simplicio-edit src/version_provenance.rs | tar -x -C fixture-base
printf 'pub const A: &str = "one";\npub const B: &str = "two";\n' > fixture-base/bench_target.rs
```

## Binaries

```bash
gh release download v3.9.2  -R simpletibr/simplicio -p simplicio-macos-arm64 -O simplicio-3.9.2  --clobber
gh release download v3.10.2 -R simpletibr/simplicio -p simplicio-macos-arm64 -O simplicio-3.10.2 --clobber
# main: build from the canonical script
SIMPLICIO_HOST_PLUGIN_BUNDLE_DIR=<bundle> ./scripts/build.sh   # then copy target/release/simplicio to simplicio-main
chmod +x simplicio-*
```

## Run

```bash
REPS=3 ./matrix.sh     # version matrix (map/context/plan/codegen/bench/mcp-cpu) -> matrix/matrix.tsv
bash fix3.sh           # context with a term present in the fixture + codegen with --repo -> matrix/fix.tsv
bash cg.sh             # codegen 3x3 -> matrix/codegen.tsv
bash cem.sh            # create/edit/measure -> cem/cem.tsv
python3 final.py       # aggregates -> matrix/final.json
```

Every script copies the fixture per rep and exports `SIMPLICIO_DAEMON_EXEC=0`,
`SIMPLICIO_TOKIO_DAEMON=0`, `SIMPLICIO_DISABLE_AUTO_UPDATE=1`, so no resident
daemon or cache survives between runs. `run.sh` is the first (polluted) draft
kept for the record; `matrix.sh` + `fix3.sh` + `cg.sh` + `cem.sh` are the ones
the reports cite.

## Notes on the numbers

- `--json` is **not** a valid flag for `codegen generate`; it publishes no JSON.
- `codegen generate` writes into `--repo`, not `--out`.
- The shell baseline is `find`, `grep -rn` and `grep -rl … | cat`; it answers the same question, not the same product.
- Peak RSS is `maximum resident set size` from `/usr/bin/time -l`.

## Agent A/B (third report)

Token and cost numbers there do not come from these scripts. They come from the
host's local database:

```sql
select cost, tokens_input, tokens_output, tokens_reasoning,
       tokens_cache_read, tokens_cache_write
from session_v2 where id = 'ses_...';
```

Two sessions with the same model and the same pinned task, one restricted to
`simplicio_*` tools and one to native tools, then compare those columns.
