#!/usr/bin/env python3
"""The same benchmark as bench.py, through the vendors' own agents: Claude Code and Grok Build.

Same prompts, same seed, same checks outside the session. Each client runs from a clean environment,
without the operator's hooks or MCP servers. "simplicio-candidate" adds one MCP server; "no-mcp" adds none.
Cost is the list price of the tokens used, the same way for both conditions. The sessions run on the
owner's own accounts, so the money is an equivalent, not what was charged.

Usage: bench_cli.py --client claude|grok --model <id> --scenario page|catalog|control --reps N --out <folder> --budget <US$>
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

import bench

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
GROK = HOME / ".grok/bin/grok"
CLAUDE = HOME / ".local/bin/claude"
PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
LABEL_MAX = 72
SEED_FILES = 3
PRICES = {
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_read": 0.1, "cache_write": 2.5},
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.2, "cache_write": 5.0},
    "grok-4.7": {"input": 2.0, "output": 6.0, "cache_read": 0.5, "cache_write": 2.0},
}


def clean(text: str) -> str:
    """One short line with no private path."""
    import re
    line = " ".join(str(text).split())
    line = re.sub(r"(/Users/[^/\s\"']+|/home/[^/\s\"']+|/private/var/folders/\S+|/var/folders/\S+|/tmp/\S+)", "<dir>", line)
    return line[:LABEL_MAX - 1] + "…" if len(line) > LABEL_MAX else line


def simplicio_name(name: str) -> str | None:
    tail = name.rsplit("__", 1)[-1]
    return tail if tail.startswith("simplicio_") else None


def claude_label(block: dict) -> tuple:
    name, inputs = block.get("name") or "tool", block.get("input") or {}
    mcp = simplicio_name(name)
    if mcp:
        return "simplicio", mcp
    if name == "Bash":
        return "tool", "$ " + clean(inputs.get("command") or "")
    path = inputs.get("file_path") or inputs.get("path")
    return "tool", name.lower() + (" " + clean(Path(str(path)).name) if path else "")


def grok_label(event: dict) -> tuple:
    name, inputs = event.get("toolName") or event.get("title") or "tool", event.get("rawInput") or {}
    mcp = simplicio_name(name)
    if mcp:
        return "simplicio", mcp
    if name in ("run_terminal_command", "shell", "bash"):
        return "tool", "$ " + clean(inputs.get("command") or inputs.get("cmd") or "")
    path = inputs.get("file_path") or inputs.get("path") or inputs.get("target_file")
    return "tool", name + (" " + clean(Path(str(path)).name) if path else "")


def stamp_seconds(text: str) -> float:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()


def price_of(tokens: dict, price: dict) -> float:
    return (tokens["input"] * price["input"] + tokens["output"] * price["output"]
            + tokens["cache_read"] * price["cache_read"] + tokens["cache_write"] * price["cache_write"]) / 1e6


def step(t0: float, t1: float, tokens: dict, tools: list, wrote: bool, price: dict) -> dict:
    return {
        "t0": round(t0, 2),
        "t1": round(t1, 2),
        "output": tokens["output"],
        "input": tokens["input"] + tokens["cache_read"] + tokens["cache_write"],
        "cost": round(price_of(tokens, price), 6),
        "tools": [{"kind": kind, "label": label} for kind, label in tools],
        "text": wrote and not tools,
        "tokens": tokens,
    }


def claude_steps(rows: list, price: dict) -> list:
    """Steps of a Claude Code transcript. A message comes in one row per block; the last holds its final usage."""
    begin = None
    previous = None
    order, merged = [], {}
    for row in rows:
        if row.get("type") not in ("user", "assistant") or not row.get("timestamp"):
            continue
        moment = stamp_seconds(row["timestamp"])
        begin = moment if begin is None else begin
        if row["type"] == "user":
            previous = moment
            continue
        message = row["message"]
        entry = merged.get(message["id"])
        if entry is None:
            entry = {"t0": (previous if previous is not None else begin) - begin, "tools": [], "wrote": False}
            merged[message["id"]] = entry
            order.append(entry)
        entry["t1"] = moment - begin
        entry["usage"] = message.get("usage") or {}
        for block in message.get("content") or []:
            if block.get("type") == "tool_use":
                entry["tools"].append(claude_label(block))
            elif block.get("type") == "text":
                entry["wrote"] = True
    steps = []
    for entry in order:
        usage = entry["usage"]
        tokens = {"input": usage.get("input_tokens") or 0, "output": usage.get("output_tokens") or 0,
                  "cache_read": usage.get("cache_read_input_tokens") or 0,
                  "cache_write": usage.get("cache_creation_input_tokens") or 0}
        steps.append(step(entry["t0"], entry["t1"], tokens, entry["tools"], entry["wrote"], price))
    return steps


def grok_steps(events: list, price: dict) -> list:
    """Steps of a Grok Build stream. A `usage` line ends a model call; the tool calls after it belong to that call."""
    steps = []
    open_from = 0.0
    last_tool_end = None
    current = None
    for moment, event in events:
        kind = event.get("type")
        if kind == "usage":
            usage = event.get("usage") or {}
            tokens = {"input": usage.get("input_tokens") or 0, "output": usage.get("output_tokens") or 0,
                      "cache_read": usage.get("cache_read_input_tokens") or 0,
                      "cache_write": usage.get("cache_creation_input_tokens") or 0}
            current = {"t0": last_tool_end if last_tool_end is not None else open_from, "t1": moment, "tokens": tokens, "tools": []}
            steps.append(current)
            last_tool_end = None
            open_from = moment
        elif kind == "tool_call" and current is not None:
            current["tools"].append(grok_label(event))
        elif kind == "tool_call_update" and event.get("status") in ("completed", "failed"):
            last_tool_end = moment
    return [step(s["t0"], s["t1"], s["tokens"], s["tools"], True, price) for s in steps]


def phase_totals(steps: list) -> dict:
    tokens = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    for item in steps:
        for key, value in item["tokens"].items():
            tokens[key] += value
    return {"requests": len(steps), "tokens": tokens, "cost": round(sum(s["cost"] for s in steps), 6)}


def spent(rows: list) -> float:
    return sum((r.get(phase) or {}).get("cost") or 0 for r in rows for phase in ("create_phase", "edit_phase"))


def client_env(extra: dict) -> dict:
    env = {"HOME": str(HOME), "PATH": PATH, "TERM": "xterm", "LANG": "en_US.UTF-8", "USER": os.environ.get("USER", ""),
           "SIMPLICIO_CANDIDATE_BIN": os.environ["SIMPLICIO_CANDIDATE_BIN"]}
    env.update(extra)
    return env


def run_process(cmd: list, env: dict, cwd: Path, clock: float) -> tuple:
    """Run one phase. Returns (exit code, wall seconds, [(session seconds, parsed line)])."""
    started = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    events = []

    def read() -> None:
        for line in proc.stdout:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                events.append((time.monotonic() - clock, json.loads(line)))
            except json.JSONDecodeError:
                pass

    reader = threading.Thread(target=read)
    reader.start()
    try:
        proc.wait(timeout=900)
    except subprocess.TimeoutExpired:
        proc.kill()
    reader.join(timeout=10)
    return proc.returncode, round(time.monotonic() - started, 3), events


def claude_session(work: Path, model: str, condition: str, prompts: tuple, config_dir: Path) -> dict:
    sid = str(uuid.uuid4())
    base = [str(CLAUDE), "-p", "--model", model, "--output-format", "stream-json", "--verbose",
            "--dangerously-skip-permissions", "--strict-mcp-config", "--setting-sources", "project"]
    if condition != "no-mcp":
        config = config_dir / "mcp.json"
        config.write_text(json.dumps({"mcpServers": {"simplicio": {"command": "/bin/bash", "args": [str(ROOT / "run_candidate.sh")]}}}))
        base += ["--mcp-config", str(config)]
    env = client_env({"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_TELEMETRY": "1"})
    clock = time.monotonic()
    create = run_process(base + ["--session-id", sid, prompts[0]], env, work, clock)
    return {"sid": sid, "create": create, "resume": lambda: run_process(base + ["--resume", sid, prompts[1]], env, work, clock)}


def claude_rows(sid: str) -> list:
    found = glob.glob(str(HOME / ".claude/projects" / "*" / (sid + ".jsonl")))
    if not found:
        return []
    return [json.loads(line) for line in Path(found[0]).read_text().splitlines() if line.strip()]


def grok_home(base: Path, condition: str) -> Path:
    home = base / "grok-home"
    shutil.rmtree(home, ignore_errors=True)
    home.mkdir(parents=True)
    (home / "auth.json").symlink_to(HOME / ".grok/auth.json")
    if condition != "no-mcp":
        (home / "config.toml").write_text(
            '[mcp_servers.simplicio]\ncommand = "/bin/bash"\nargs = ["%s"]\nenabled = true\n' % (ROOT / "run_candidate.sh"))
    return home


def grok_session(work: Path, model: str, condition: str, prompts: tuple, config_dir: Path) -> dict:
    sid = str(uuid.uuid4())
    home = grok_home(config_dir, condition)
    base = [str(GROK), "-m", model, "--output-format", "streaming-json", "--always-approve", "--disable-web-search",
            "--no-subagents", "--cwd", str(work)]
    env = client_env({"GROK_HOME": str(home), "GROK_CLAUDE_MCPS_ENABLED": "0", "GROK_CURSOR_MCPS_ENABLED": "0",
                      "GROK_MANAGED_MCPS_ENABLED": "0"})
    clock = time.monotonic()
    create = run_process(base + ["--session-id", sid, "-p", prompts[0]], env, work, clock)
    return {"sid": sid, "create": create, "resume": lambda: run_process(base + ["--resume", sid, "-p", prompts[1]], env, work, clock)}


def run_one(client: str, model: str, condition: str, rep: int, scenario: str, price: dict) -> dict:
    create_prompt, edit_prompt, check, data_name, data_rows = bench.SCENARIOS[scenario]
    base = Path(tempfile.mkdtemp(prefix="bench-cli-"))
    work = base / "work"
    config_dir = base / "config"
    config_dir.mkdir()
    bench.seed_work(work, data_name, data_rows)
    (work / "opencode.json").unlink(missing_ok=True)
    session = (claude_session if client == "claude" else grok_session)(work, model, condition, (create_prompt, edit_prompt), config_dir)
    code, wall, create_events = session["create"]
    created = check(work, edited=False)
    edit_code, edit_wall, edit_events = session["resume"]()
    edited = check(work, edited=True)
    if client == "claude":
        steps = claude_steps(claude_rows(session["sid"]), price)
        split = None
    else:
        steps = grok_steps(create_events + edit_events, price)
        split = len(grok_steps(create_events, price))
    middle = split if split is not None else len(steps)
    if client == "claude":
        boundary = wall
        middle = sum(1 for item in steps if item["t0"] <= boundary)
    delivered = os.environ.get("BENCH_DELIVERED")
    if delivered:
        bench.keep_delivered(work, Path(delivered) / ("%s-rep-%02d" % (condition, rep)), data_name)
    shutil.rmtree(base, ignore_errors=True)
    return {
        "condition": condition,
        "rep": rep,
        "client": client,
        "model": model,
        "create_run": {"exit": code, "wall_s": wall, "session_id": session["sid"]},
        "edit_run": {"exit": edit_code, "wall_s": edit_wall, "session_id": session["sid"]},
        "create_phase": phase_totals(steps[:middle]),
        "edit_phase": phase_totals(steps[middle:]),
        "session": {"id": session["sid"]},
        "steps": steps,
        "files_after_create": created,
        "files_after_edit": edited,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", choices=("claude", "grok"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--scenario", choices=sorted(bench.SCENARIOS), required=True)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--budget", type=float, required=True, help="list price in US$ for this folder")
    args = parser.parse_args()
    price = PRICES[args.model]
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / "results.json"
    rows = json.loads(path.read_text()) if path.exists() else []
    for rep in range(args.reps):
        for condition in ("no-mcp", "simplicio-candidate"):
            if any(r["condition"] == condition and r["rep"] == rep for r in rows):
                continue
            if spent(rows) >= args.budget:
                print("STOP: budget reached", round(spent(rows), 4), flush=True)
                return 4
            print(time.strftime("%H:%M:%S"), args.client, args.scenario, condition, "rep", rep, flush=True)
            record = run_one(args.client, args.model, condition, rep, args.scenario, price)
            rows.append(record)
            path.write_text(json.dumps(rows, indent=1) + "\n")
            print(json.dumps({"wall": [record["create_run"]["wall_s"], record["edit_run"]["wall_s"]],
                              "requests": len(record["steps"]), "cost": round(spent([record]), 4),
                              "ok": [record["files_after_create"].get("ok"), record["files_after_edit"].get("ok")]}), flush=True)
    print("done, spent", round(spent(rows), 4), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
