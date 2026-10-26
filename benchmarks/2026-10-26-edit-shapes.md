# Edition shapes: map + edit, codegen-driven, and a loose file (2026-10-26)

Third measurement of the day. The other two answered "how fast is each surface" and "how fast is the create/edit/measure loop". This one answers the owner's question: **can the runtime edit a project, edit it through codegen, and edit a single loose file — and how do the versions compare?**

Three edition shapes, same fixture, three builds, 3 reps, daemon off, no network:

1. **`map` + `edit`** — orient the project with `map`, then apply a deterministic edit to a project file.
2. **codegen-driven** — change the contract (one new field) and regenerate the project with `codegen generate`.
3. **loose file** — edit a single file that is **not** inside a git repository.

Every run was checked for the expected bytes; correctness is reported per shape.

## Results (median of 3)

| phase | v3.9.2 | v3.10.2 | main | no-Simplicio |
|---|---|---|---|---|
| **create** — `codegen generate` (1 contract → 2 files) | 0.06 s · 10.1 MB | 0.09 s · 11.8 MB | 0.12 s · 12.0 MB | 0.00 s (heredoc) |
| **edit via `map`** — `map --repo` | 4.59 s · 34.4 MB · 23,452 B | 0.37 s · 35.1 MB · 4,959 B | **0.29 s** · 36.0 MB · 4,945 B | 0.05 s (`grep -rn`) |
| **edit via `map`** — `edit '<plan>'` | 2.78 s · 34.3 MB | 0.29 s · 35.7 MB | **0.31 s** · 36.2 MB | — |
| **edit via `map`** — total | **7.37 s** | **0.66 s** | **0.60 s** | ~0.05 s |
| **codegen-driven edition** — new contract field → regenerate | 0.05 s · 10.1 MB | 0.10 s · 11.9 MB | 0.17 s · 12.1 MB | — |
| **loose file edition** — `edit` outside any repo | 2.80 s · 34.3 MB | 0.31 s · 35.6 MB | **0.32 s** · 36.3 MB | 0.02 s (`python` replace) |
| **measure** — `context --term memory` | 0.08 s · 13,750 B | 0.21 s · 28,572 B | 0.23 s · 28,560 B | 0.09 s · **1,196,832 B** |

Correctness (expected bytes present after the phase): **all shapes passed on all three versions** — `edit via map` 3/3, `codegen-driven` 3/3, `loose file` 3/3. The native baseline also passed its two equivalent shapes.

## What this says

- **Edition with `map` is 11-12x faster** than 3.9.2: 7.37 s → 0.66 s (3.10.2) and 0.60 s (main). The `map` itself is the whole difference: 4.59 s → 0.29-0.37 s, and the edit applies in 0.29-0.31 s instead of 2.78 s.
- **A loose file is edited in 0.31-0.32 s**, 9x faster than 3.9.2, and it works without a repository — `--repo <directory>` is enough. This was the `fix/edit-without-git` case; it holds on all three builds.
- **Codegen-driven edition works on all three** (the regenerated sources contain the new field), but it is **slower on the newer builds** in this harness: 0.05 s (3.9.2) → 0.10 s (3.10.2) → 0.17 s (main). An isolated first-generation run measured 0.01 s for 3.10.2/main, so the cost appears when regenerating over existing output (binding scan + rewrite), not on a clean generate. Treat 0.01-0.17 s as the range and measure before claiming a speedup.
- **Measurement is the one place 3.9.2 wins**: 13.7 KB and 0.08 s vs 28.6 KB and 0.21-0.23 s. The newer packet is still 42x smaller than reading the matching files raw (1,196,832 B), so the token-economy claim holds, but the newer versions return twice as much as 3.9.2.
- **The shell is faster everywhere** because it does none of the work: no receipt, no governed writer, no bounded packet, no map. It is the correct baseline for "bytes handed to the caller", not a competitor for capability.

## The four edition lanes, for the fast-path document

| need | command | measured |
|---|---|---|
| edit a file in a project | `map --repo .` → `edit '<plan>' --repo . --json` | 0.60-0.66 s total |
| generate or regenerate from a contract | `codegen generate --schema <file> --lang <lang> --repo .` | 0.01-0.17 s |
| edit a file outside any repo | `edit '<plan>' --repo <dir> --json` | 0.31-0.32 s |
| verify after any of them | `shell` / `benchmark run` | 0.01 s / 0.42 s |

## Caveats

- Fixture is 65 files; `map` on a 1,000-file repository will not be 0.3 s.
- Codegen timings vary with whether the output already exists (0.01 s clean vs 0.10-0.17 s regenerate); the harness records both.
- The shell baseline does not produce receipts, preimages or a governed write, so its 0.02-0.05 s is not an equivalent delivery.
- `edit` with `--repo` pointing at a plain directory (no git) is supported; do not assume a repository is required.

## Reproduce

```bash
bash harness-2026-10-26/edit3.sh     # -> editbench/edit.tsv
```

The script seeds a fresh `git init` copy per rep, builds `api2.json` with one extra field, runs the three edition shapes plus creation and measurement for each version, and records correctness per shape.
