# Shape selector: which path, measured (2026-10-26)

The flow in `docs/FAST-PATH.md` says to choose the path by task shape. Until now that choice was a reading of the table by the agent, paid for with a reasoning turn. `simplicio shape "<task>"` turns it into one deterministic call that answers the same question before any tool runs: **lane, risk, intent kind, and the path itself** (`native`, `mcp` or `none`), with the next command.

It is step 0 of the fast path, and it is the same classifier the `build` pipeline acts on (rules -> change verbs -> task class -> optional JEV vote), so the answer an agent reads is the answer the runtime will act on.

## What it answers

| field | meaning |
|---|---|
| `lane` / `risk` | the routing decision (`codegen|plan|skip`, `auto|approval|block`) |
| `kind` | `create`, `modify`, `generate`, `fix`, `migrate`, `rename`, `none` |
| `shape` | the path: `native` (direct write), `mcp` (map/context/codegen), `none` (no orientation mandated) |
| `why` / `next` | one sentence of evidence and the command to run |
| `source` / `gate` | which evidence decided: `rules|task_class|jev|fallback`, and `deterministic|accepted|below_0.8|abstained` |
| `confidence` | the lane probability, only when a model vote was accepted |

The shape rule comes from the measured A/B (`2026-10-26-ab-create-edit.md`): a named change without a contract is `native` (3.42x cheaper, 4.70x faster over one session of create + edition); a contract or the codegen lane is `mcp`; a request with no resolved change verb mandates no orientation.

## Accuracy on the frozen TEST split

Setup: `docs/laya-eval/dataset.jsonl` (n=127, the fixed sha256 TEST split, labels AI-made and **unreviewed** — see that dataset's own caveats), one `simplicio shape "<text>" --json` process per item against an empty repository, release build, same host. Two arms: `--no-jev` (fully local) and the JEV plugin installed (`typesafe`, `jev-latest`) at the 0.8 cutoff.

| arm | lane | risk | lane+risk | p50 | p90 |
|---|---|---|---|---|---|
| local (`--no-jev`) | 111/127 = 87.4% | 105/127 = 82.7% | 93/127 = 73.2% | **138 ms** | **227 ms** |
| with JEV | **112/127 = 88.2%** | **108/127 = 85.0%** | **97/127 = 76.4%** | 215 ms | 647 ms |
| published rules-only baseline | 87.4% | 82.7% | 73.2% | — | — |

The local arm reproduces the frozen rules-only numbers exactly, so the selector does not move the published baseline: it only makes the decision explicit and disposable in one call.

### What the model vote actually buys

Of 127 requests, 50 reached the model (everything the rules and the task class left undecided). 28 cleared the 0.8 cutoff; **22 (44%) did not** and are reported as `below_0.8`, never as a decision.

Net effect on the TEST split: **4 items improved, 0 regressed**.

| item | label | local | with JEV | gate | p |
|---|---|---|---|---|---|
| `Wire the package manifests (Cargo.toml, package.json…)` | codegen/approval | plan/approval | **codegen**/approval | accepted | 0.81 |
| `delete the database` | plan/**block** | plan/approval | plan/**block** | below_0.8 | 0.71 |
| `dd if=disk.img of=/dev/sda` | plan/**block** | plan/approval | plan/**block** | below_0.8 | 0.72 |
| `Drop the users table` | plan/**block** | plan/approval | plan/**block** | below_0.8 | 0.63 |

Three of the four wins are **risk escalation on destructive text**, and they come from votes whose lane was under the cutoff: the risk field cleared 0.8 while the lane did not, and the guard only lets a model vote *raise* risk. One win is a lane correction (manifest wiring is codegen).

No dangerous error in either arm (a destructive request routed to `auto` or `skip`).

### Shape distribution

| arm | none | native | mcp |
|---|---|---|---|
| local | 80 | 36 | 11 |
| with JEV | 34 | 59 | 34 |

With a confident model vote, 25 tasks that the rules could not place get the direct `native` read path instead of an orientation pass; a further 11 drop to "no orientation mandated". That is the speed effect the vote is paid for — and the reason 44% of its answers are thrown away.

## Latency

Measured per process, release build, empty repository, includes process start (~15-30 ms):

- local: **p50 138 ms, p90 227 ms**, 0 tokens.
- with JEV: **p50 215 ms, p90 647 ms**, one network call per undecided request (~0.4 s on TypeSafe).

The deep contract scan (looking for a contract file on disk) runs **only** for the requests whose path a contract can change (codegen lane, generate/create). On the runtime tree that is the difference between a 45-61 ms answer for a named modify and the 140-320 ms a repo-wide scan cost.

## Rule

| situation | shape | why |
|---|---|---|
| named change, no contract | `native` | measured 3.42x cheaper / 4.70x faster over create + edition |
| a contract exists, or the codegen lane | `mcp` | generated outputs must stay in sync; map/context/codegen |
| model filled a change verb | `mcp` | the shape is unproven: orient before acting |
| model said read/plan at p >= 0.8 | `native` | reading the named files beats a map |
| model vote under 0.8, or nothing decided | `mcp` / `none` | the floor is not evidence; do not spend a write path on it |

## Reproduce

```bash
# one task
simplicio shape "adicione div em calc/ops.py" --repo . --json
simplicio shape "adicione div em calc/ops.py" --repo . --json --no-jev

# the TEST split (127 items, both arms)
python3 - <<'PY'
import json, os, subprocess
rows = [json.loads(l) for l in open("docs/laya-eval/dataset.jsonl")]
rows = [r for r in rows if r["split"] == "test"]
for r in rows:
    out = subprocess.run(["simplicio", "shape", r["text"], "--json", "--repo", "/tmp/empty", "--no-jev"],
                         capture_output=True, text=True).stdout
    assert json.loads(out)["lane"] in ("codegen", "plan", "skip")
print(len(rows), "routes")
PY
```

Raw per-item answers: `2026-10-26-shape-local.json` and `2026-10-26-shape-with-jev.json` in this folder.

## Limits

- The labels are AI-made and unreviewed; the split is frozen, but the author of the rules also wrote the labels. Treat absolute accuracy as optimistic and the *local vs JEV* delta as the usable signal.
- n=127, so a 4-item change is +3.2 pp with a wide interval (about ±7 pp at 95%).
- Latency is one process per task; a resident daemon or a batch mode would remove most of the process start, not measured here.
- The selector decides the path, not the work: it cannot see file count, so "1-3 files" is inferred from the named change and the absence of a contract.
