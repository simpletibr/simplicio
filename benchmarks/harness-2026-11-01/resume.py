#!/usr/bin/env python3
"""Runs the sessions a benchmark round still lacks, and waits out the provider limit by itself.

One session at a time, through bench.py, so a stop never loses more than the session in progress.
Sessions already saved are never repeated. Conditions alternate per repetition.

Usage:
  python3 resume.py --conditions a,b,c --model <model> --round page:<folder>:10 --round control:<folder>:6
Exit code 0 when every round is complete, 1 otherwise.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIMIT_EXIT = 3
MAX_ATTEMPTS = 3
WAIT_MARGIN_S = 90
DEFAULT_WAIT_S = 900
SIMPLICIO = Path.home() / ".local" / "bin" / "simplicio"


@dataclass
class Round:
    scenario: str
    out: Path
    reps: int
    conditions: list | None = None


def log(*parts) -> None:
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


def missing(out: Path, conditions: list, reps: int) -> list:
    """(rep, condition) pairs without a valid saved session, one repetition of each condition at a time."""
    path = out / "results.json"
    rows = json.loads(path.read_text()) if path.exists() else []
    done = {(r.get("condition"), r.get("rep")) for r in rows if not r.get("error") and r.get("create_run")}
    return [(rep, condition) for rep in range(reps) for condition in conditions if (condition, rep) not in done]


def wait_from_output(output: str) -> int | None:
    found = re.findall(r"retry_after_ms=(\d+)", output)
    return int(found[-1]) if found else None


def login_ok() -> bool:
    """A broken login degrades every MCP condition silently, so no session may start without one."""
    try:
        done = subprocess.run([str(SIMPLICIO), "auth", "status", "--json"], capture_output=True, text=True, timeout=60)
        return json.loads(done.stdout).get("ok") is True
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def run_session(round_: Round, rep: int, condition: str, model: str) -> tuple:
    """Exit code of one session, and the wait the provider asked for when it hit the limit."""
    done = subprocess.run(
        [sys.executable, str(ROOT / "bench.py"), "--scenario", round_.scenario, "--start", str(rep), "--reps", "1",
         "--conditions", condition, "--model", model, "--out", str(round_.out)],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    return done.returncode, wait_from_output(done.stdout)


def run_round(round_: Round, conditions: list, model: str) -> bool:
    attempts = Counter()
    while True:
        pending = missing(round_.out, conditions, round_.reps)
        todo = [pair for pair in pending if attempts[pair] < MAX_ATTEMPTS]
        if not todo:
            log("round", round_.scenario, "finished; sessions left:", pending)
            return not pending
        if not login_ok():
            log("STOP: the Simplicio login is not valid; no session started")
            return False
        rep, condition = todo[0]
        log("session", round_.scenario, condition, "rep", rep)
        code, wait_ms = run_session(round_, rep, condition, model)
        if code == LIMIT_EXIT:
            wait_s = wait_ms // 1000 + WAIT_MARGIN_S if wait_ms is not None else DEFAULT_WAIT_S
            log("provider limit; waiting", wait_s, "s")
            time.sleep(wait_s)
            continue
        attempts[(rep, condition)] += 1
        log("session exit", code)


def parse_round(text: str) -> Round:
    scenario, out, reps, *own = text.split(":")
    return Round(scenario, Path(out), int(reps), own[0].split(",") if own else None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conditions", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--round", dest="rounds", action="append", type=parse_round, required=True)
    args = parser.parse_args()
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    complete = [run_round(round_, round_.conditions or conditions, args.model) for round_ in args.rounds]
    log("resume done:", "complete" if all(complete) else "incomplete")
    return 0 if all(complete) else 1


if __name__ == "__main__":
    raise SystemExit(main())
