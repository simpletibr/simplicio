#!/usr/bin/env python3
"""Build assets/data/simplicio-bench.json for the site from the benchmark artifacts.

Medians come from every session of a round. Each replay is the delivered session closest to the median
time, chosen here and never by hand. A model appears only when it has sessions in both conditions.

Usage: site_bench.py <out json>
"""
import json
import re
import statistics
import sys
from pathlib import Path

import replay

BENCH = HERE = Path(__file__).parent
# Order asked by the owner. DeepSeek keeps the published 2026-10-31 round: its 2026-11-01 rerun shared work
# folders with another harness, so it was discarded.
ROUNDS = [
    ("anthropic/claude-sonnet-5.5", "Claude Sonnet 5.5 · Claude Code", BENCH / "artifacts-2026-11-01-claude-sonnet-5.5"),
    ("x-ai/grok-4.7", "Grok 4.7 · Grok Build", BENCH / "artifacts-2026-11-01-grok-4.7"),
    ("anthropic/claude-haiku-5.5", "Claude Haiku 5.5 · OpenCode", BENCH / "artifacts-2026-11-01-claude-haiku-5.5"),
    ("deepseek/deepseek-v4.1-flash-1017", "DeepSeek V4.1 Flash · OpenCode", HERE / "or-2026-10-31"),
]
TASKS = {
    "page": ("page", ["Page from a JSON file, a generator covers it", "Página a partir de um JSON, coberta por um gerador"]),
    "newpage": ("catalog", ["New page, other data, other language", "Página nova, outros dados e outro idioma"]),
    "script": ("control", ["Python script, no generator covers it", "Script Python, sem gerador que cubra"]),
}
CONDITIONS = {"with": "simplicio-candidate", "without": "no-mcp", "v392": "simplicio-3.9.2"}


def total_tokens(record: dict, price: dict) -> dict:
    tokens = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    requests = 0
    for phase in ("create_phase", "edit_phase"):
        data = record.get(phase) or {}
        requests += data.get("requests") or 0
        for key, value in (data.get("tokens") or {}).items():
            tokens[key] += value
    cost = (tokens["input"] * price["input"] + (tokens["output"] + tokens["reasoning"]) * price["output"]
            + tokens["cache_read"] * price["cache_read"] + tokens["cache_write"] * price["cache_write"]) / 1e6
    # Reasoning is billed as output, and the replay and the published report count it the same way.
    return {"requests": requests, "output_tokens": tokens["output"] + tokens["reasoning"], "cost_usd": cost}


def summary(records: list, price: dict) -> dict:
    rows = [total_tokens(r, price) for r in records]
    return {
        "n": len(records),
        "seconds": round(statistics.median(replay.session_seconds(r) for r in records), 1),
        "requests": statistics.median(r["requests"] for r in rows),
        "output_tokens": int(statistics.median(r["output_tokens"] for r in rows) + 0.5),
        "cost_usd": round(statistics.median(r["cost_usd"] for r in rows), 6),
        "delivered": sum(1 for r in records if replay.delivered(r)),
    }


def compact(steps: list) -> list:
    """Short keys, because this file loads with the landing."""
    out = []
    for step in steps:
        labels = [["s" if tool["kind"] == "simplicio" else "t", tool["label"].replace("~", "<dir>")] for tool in step["tools"]]
        out.append({"a": step["t0"], "b": step["t1"], "o": step["output"], "c": step["cost"], "l": labels})
    return out


def build_condition(records: list, price: dict) -> dict:
    data = summary(records, price)
    chosen = replay.median_session(records)
    if chosen.get("steps"):
        built = {"steps": chosen["steps"], "total": {"seconds": chosen["steps"][-1]["t1"]}}
    else:
        built = replay.steps_from_rows(replay.session_rows(chosen["create_run"]["session_id"]), price)
    data["replay"] = {"rep": chosen["rep"], "seconds": built["total"]["seconds"], "steps": compact(built["steps"])}
    data["chosen_rep"] = chosen["rep"]
    return data


def task_block(folder: Path, title: list, price: dict) -> dict | None:
    path = folder / "results.json"
    if not path.exists():
        return None
    records = [r for r in json.loads(path.read_text()) if r.get("create_run") and r.get("session")]
    block = {"title": title}
    for key, name in CONDITIONS.items():
        rows = [r for r in records if r["condition"] == name]
        if rows:
            block[key] = build_condition(rows, price)
    return block if "with" in block and ("without" in block or "v392" in block) else None


def publish_delivered(root: Path, model: str, tasks: dict, target: Path) -> None:
    """Copy the page each side delivered in the replayed session, so a visitor can use it."""
    pages = {"page": "users.html", "newpage": "catalog.html"}
    folder = target.parent.parent / "bench" / model.split("/")[1]
    for key, name in pages.items():
        for side, condition in (("with", "simplicio-candidate"), ("without", "no-mcp")):
            data = tasks.get(key, {}).get(side)
            if not data:
                continue
            source = root / "delivered" / ("%s-rep-%02d" % (condition, data["chosen_rep"])) / name
            if not source.exists():
                continue
            out = folder / ("%s-%s.html" % (key, side))
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(source.read_bytes())
            data["delivered_url"] = "/assets/bench/%s/%s" % (model.split("/")[1], out.name)


def video_entries(target: Path, models: list) -> list:
    """Videos on disk for the published models. A task without its video and poster is left out."""
    folder = target.parent.parent / "videos" / "bench"
    entries = []
    for model in models:
        stem = re.sub(r"-\d{4}$", "", model["id"].split("/")[1])
        for task in model["tasks"]:
            name = "%s-%s" % (stem, task)
            if (folder / (name + ".mp4")).exists() and (folder / (name + ".png")).exists():
                entries.append({"model": model["id"], "task": task, "poster": "/assets/videos/bench/%s.png" % name,
                                "src": "/assets/videos/bench/%s.mp4" % name})
    return entries


def main() -> int:
    target = Path(sys.argv[1])
    models = []
    for model, name, root in ROUNDS:
        if not root.exists():
            continue
        _, price = replay.load_route(model)
        tasks = {}
        for key, (folder, title) in TASKS.items():
            block = task_block(root / folder, title, price)
            if block:
                tasks[key] = block
        if "page" not in tasks:
            continue
        sessions = sum(task[c]["n"] for task in tasks.values() for c in CONDITIONS if c in task)
        publish_delivered(root, model, tasks, target)
        models.append({"id": model, "name": name, "sessions": sessions, "tasks": tasks,
                       "endpoint_note": "OpenRouter"})
        print(name, sessions, {k: (v["with"]["seconds"], (v.get("without") or v.get("v392"))["seconds"]) for k, v in tasks.items()})
    out = {"schema": "simplicio.site-bench/v1", "version": "3.10.8", "client": "OpenCode 2.1.4", "models": models,
           "videos": video_entries(target, models)}
    target.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("wrote", target, target.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
