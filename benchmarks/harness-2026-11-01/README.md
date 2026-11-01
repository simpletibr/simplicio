# Harness for the 2026-11-01 measurements

This produced [`../2026-11-01-multi-model.md`](../2026-11-01-multi-model.md). Per-session data is in [`../2026-11-01-multi-model.json`](../2026-11-01-multi-model.json). The artifact folders with full session records are not here.

Python 3 standard library, plus Google Chrome for the delivery check.

| File | What it does |
|---|---|
| `bench.py` | One OpenCode session per run, against a private server, in its own folder |
| `resume.py` | Runs the sessions a round still lacks, one at a time, and waits out provider limits |
| `bench_cli.py` | The same sessions headless in Claude Code and Grok Build, with a spending cap per task |
| `check_page.py` | Delivery check outside the session: opens the page in headless Chrome and uses it |
| `run_candidate.sh` | Starts the Runtime build under test as the MCP server |
| `replay.py` | Turns a session into timed steps, with private paths removed from the labels |
| `site_bench.py` | Builds the site's data file from the rounds |
| `site_evidence.py` | Builds the report, its session data and the site's evidence files |
| `prices.json` | List price and fixed endpoint of each model |

## Run

```bash
export SIMPLICIO_CANDIDATE_BIN=/path/to/simplicio

# OpenCode through OpenRouter
export OPENROUTER_API_KEY=...
export BENCH_DELIVERED="$PWD/round/delivered"
python3 resume.py --conditions no-mcp,simplicio-candidate --model openrouter/anthropic/claude-haiku-5.5 \
  --round page:round/page:5 --round catalog:round/catalog:5 --round control:round/control:5

# Claude Code or Grok Build, on the account already logged in
python3 bench_cli.py --client claude --model claude-sonnet-5-5 --scenario page --reps 5 --out round/page --budget 2.5
```

Run one queue at a time. Each session has its own folder, so two queues no longer corrupt each other, but they share the machine and the provider, and the times stop being comparable.

`BENCH_STATE` moves the state folder. `BENCH_SANDBOX` names a folder with a `run.sh` launcher, needed only for a `simplicio-<version>` condition. `SITE_ROOT` is the site checkout for `site_evidence.py`, and `site_bench.py` reads the round folders named in its `ROUNDS` table.

## Test

```bash
python3 -m unittest test_bench test_bench_cli test_replay test_resume
```
