#!/usr/bin/env python3
"""Turn real OpenCode sessions into replay files for the site and the videos.

A replay holds what happened and when: each model request with its tokens, and each tool call with a
short label. It holds no tool output, no file content and no absolute path. Cost comes from the tokens
at the prices of the model's fixed endpoint, so every model is priced the same way.

Usage: replay.py <artifacts folder> <model id> <out folder>
It picks, for each task and condition, the delivered session closest to the median time, so the replay
shown is neither the best nor the worst run.
"""
import json
import os
import re
import sqlite3
import statistics
import sys
from pathlib import Path

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
HOME = re.compile(r"(/Users/[^/\s\"']+|/home/[^/\s\"']+|/private/var/folders/\S+|/var/folders/\S+|/tmp/\S+)")
SIMPLICIO_CALL = re.compile(r"simplicio_([a-z0-9_]+)\s*\(")
LABEL_MAX = 72


def clean(text: str) -> str:
    """One short line with no private path."""
    line = " ".join(str(text).split())
    line = HOME.sub("<dir>", line)
    return line[:LABEL_MAX - 1] + "…" if len(line) > LABEL_MAX else line


def tool_label(item: dict) -> tuple:
    """(kind, label) of one tool part."""
    name = item.get("name") or "tool"
    inputs = (item.get("state") or {}).get("input") or {}
    if name == "execute":
        calls = SIMPLICIO_CALL.findall(inputs.get("code") or "")
        if calls:
            return "simplicio", "simplicio_" + calls[0]
        return "tool", "execute"
    if name.startswith("simplicio_"):
        return "simplicio", name
    if name == "shell":
        return "tool", "$ " + clean(inputs.get("command") or "")
    path = inputs.get("filePath") or inputs.get("path") or inputs.get("file")
    return "tool", name + (" " + clean(Path(str(path)).name) if path else "")


def cost_of(tokens: dict, price: dict) -> float:
    """US$ of one request. `price` is per million tokens."""
    cache = tokens.get("cache") or {}
    return (
        (tokens.get("input") or 0) * price["input"]
        + ((tokens.get("output") or 0) + (tokens.get("reasoning") or 0)) * price["output"]
        + (cache.get("read") or 0) * price["cache_read"]
        + (cache.get("write") or 0) * price["cache_write"]
    ) / 1_000_000


def steps_from_rows(rows: list, price: dict) -> dict:
    """Build the replay of a session from its `session_message` rows, oldest first."""
    assistants = []
    for kind, data in rows:
        if kind != "assistant":
            continue
        parsed = json.loads(data)
        timing = parsed.get("time") or {}
        if timing.get("created") and (timing.get("completed") or timing.get("streamed")):
            assistants.append(parsed)
    if not assistants:
        return {"steps": [], "total": {"seconds": 0, "requests": 0, "output_tokens": 0, "input_tokens": 0, "cost_usd": 0}}
    start = assistants[0]["time"]["created"]
    steps = []
    output_total = input_total = 0
    cost_total = 0.0
    for parsed in assistants:
        timing, tokens = parsed["time"], parsed.get("tokens") or {}
        cache = tokens.get("cache") or {}
        cost = cost_of(tokens, price)
        output = (tokens.get("output") or 0) + (tokens.get("reasoning") or 0)
        sent = (tokens.get("input") or 0) + (cache.get("read") or 0) + (cache.get("write") or 0)
        output_total += output
        input_total += sent
        cost_total += cost
        end = timing.get("completed") or timing.get("streamed")
        tools = [tool_label(item) for item in parsed.get("content") or []
                 if isinstance(item, dict) and item.get("type") == "tool"]
        wrote = sum(len(str(item.get("text") or "")) for item in parsed.get("content") or []
                    if isinstance(item, dict) and item.get("type") == "text")
        steps.append({
            "t0": round((timing["created"] - start) / 1000, 2),
            "t1": round((end - start) / 1000, 2),
            "output": output,
            "input": sent,
            "cost": round(cost, 6),
            "tools": [{"kind": kind, "label": label} for kind, label in tools],
            "text": wrote > 0 and not tools,
        })
    return {
        "steps": steps,
        "total": {
            "seconds": steps[-1]["t1"],
            "requests": len(steps),
            "output_tokens": output_total,
            "input_tokens": input_total,
            "cost_usd": round(cost_total, 6),
        },
    }


def session_rows(session_id: str) -> list:
    con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    return list(con.execute(
        "select type, data from session_message where session_id=? order by seq", (session_id,)))


def session_seconds(record: dict) -> float:
    return (record["create_run"]["wall_s"] or 0) + (record["edit_run"]["wall_s"] or 0)


def delivered(record: dict) -> bool:
    return all((record.get(key) or {}).get("ok") for key in ("files_after_create", "files_after_edit"))


def median_session(records: list) -> dict:
    """The delivered session closest to the median time of the delivered sessions."""
    good = [r for r in records if delivered(r)] or records
    middle = statistics.median(session_seconds(r) for r in good)
    return min(good, key=lambda r: (abs(session_seconds(r) - middle), r["rep"]))


def load_route(model: str) -> tuple:
    """(endpoint, price per million tokens) of a model, fixed for its whole round."""
    entry = json.loads(Path(__file__).with_name("prices.json").read_text())[model]
    return entry["endpoint"], entry["price"]


def main() -> int:
    root, model, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    tag, price = load_route(model)
    out.mkdir(parents=True, exist_ok=True)
    for task_dir in sorted(p for p in root.iterdir() if (p / "results.json").exists()):
        records = [r for r in json.loads((task_dir / "results.json").read_text()) if r.get("create_run")]
        for condition in sorted({r["condition"] for r in records}):
            chosen = median_session([r for r in records if r["condition"] == condition])
            replay = steps_from_rows(session_rows(chosen["create_run"]["session_id"]), price)
            replay.update({
                "schema": "simplicio.bench-replay/v1",
                "model": model,
                "endpoint": tag,
                "task": task_dir.name,
                "condition": condition,
                "rep": chosen["rep"],
                "delivered": delivered(chosen),
                "price_usd_per_million": price,
            })
            target = out / ("%s-%s-%s.json" % (model.replace("/", "_"), task_dir.name, condition))
            target.write_text(json.dumps(replay, ensure_ascii=False, separators=(",", ":")) + "\n")
            print(target.name, replay["total"], "steps", len(replay["steps"]), "delivered", replay["delivered"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
