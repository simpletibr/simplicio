#!/usr/bin/env python3
"""Publish one measured round from one source: site evidence, WebMCP tool and public report.

Medians come from assets/data/simplicio-bench.json, session rows from the round folders.

Usage: site_evidence.py <public repository checkout>
"""
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

import replay
import site_bench

SITE = Path(os.environ.get("SITE_ROOT", "."))
DATE = "2026-11-01"
STEM = f"{DATE}-multi-model"
BASE = "https://github.com/simpletibr/simplicio/blob/master/benchmarks/"
REPORT = BASE + STEM + ".md"
SETUPS = (("with", "Simplicio 3.10.8"), ("without", "No MCP"), ("v392", "Simplicio 3.9.2"))
TASKS = (("page", "Page from a JSON file, a generator covers it"),
         ("newpage", "New page, other data, other language, not used to build the generator"),
         ("script", "Python script, no generator covers it"))
CLIENTS = {
    "anthropic/claude-sonnet-5.5": "Claude Code 2.1.316",
    "x-ai/grok-4.7": "Grok Build 1.0.46",
    "anthropic/claude-haiku-5.5": "OpenCode 2.1.4",
    "deepseek/deepseek-v4.1-flash-1017": "OpenCode 2.1.4",
}
LIMITS = [
    "The gain comes from the generator. On a task no generator covers, Simplicio can cost more than no MCP at all.",
    "A valid request the closed scope does not recognise takes the slower path: 10 of 15 valid requests reached "
    "the generator on a frozen set.",
    "Each model ran in one client, so compare a model with itself, not one model with another.",
    "Few sessions on three small tasks. Other tasks and models will give other numbers.",
]


def short(name: str) -> str:
    return name.split(" · ")[0]


def rows_of(model: dict) -> list:
    """One entry per task, with the results in the order the report shows them."""
    tasks = []
    for key, title in TASKS:
        task = model["tasks"].get(key)
        if not task:
            continue
        results = [{"setup": setup, "n": task[side]["n"], "seconds": task[side]["seconds"],
                    "requests": task[side]["requests"], "output_tokens": task[side]["output_tokens"],
                    "cost_usd": round(task[side]["cost_usd"], 4), "delivered": task[side]["delivered"]}
                   for side, setup in SETUPS if side in task]
        tasks.append({"id": key, "title": title, "results": results})
    return tasks


def entry(data: dict) -> dict:
    return {
        "id": "multi-model-" + DATE,
        "date": DATE,
        "status": "MEASURED",
        "report": REPORT,
        "session_data": BASE + STEM + ".json",
        "simplicio": data["version"],
        "statistic": "median",
        "sessions": sum(model["sessions"] for model in data["models"]),
        "models": [{"id": model["id"], "name": short(model["name"]), "client": CLIENTS[model["id"]],
                    "price_usd_per_million_tokens": replay.load_route(model["id"])[1], "tasks": rows_of(model)}
                   for model in data["models"]],
    }


def write_dataset(run: dict) -> None:
    path = SITE / "data/benchmarks/benchmark-v1.json"
    dataset = json.loads(path.read_text())
    dataset["dataset_id"] = "site-simpleti-public-evidence-" + DATE
    dataset["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    kept = [item for item in dataset["agent_benchmarks"] if item["id"] != run["id"]]
    dataset["agent_benchmarks"] = [run] + kept
    path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n")


def write_webmcp(run: dict) -> None:
    path = SITE / "assets/js/simplicio-webmcp.js"
    source = path.read_text()
    source, swapped = re.subn(r"const report = '[^']+';", f"const report = '{REPORT}';", source)
    assert swapped == 1
    answer = {
        "date": DATE, "simplicio": run["simplicio"], "statistic": "median", "sessions": run["sessions"],
        "models": [{"name": model["name"], "client": model["client"],
                    "tasks": [{"task": task["title"], "results": task["results"]} for task in model["tasks"]]}
                   for model in run["models"]],
        "limitations": LIMITS,
    }
    names = " and ".join([", ".join(model["name"] for model in run["models"][:-1]), run["models"][-1]["name"]])
    tool = (f" {{name:'simplicio_benchmark',description:'Read the public {DATE} benchmark of Simplicio "
            f"{run['simplicio']} with {names}, with and without Simplicio, with medians per task and limitations.',"
            "inputSchema:empty,\n execute:async()=>output({date:" + repr(DATE) + ","
            + json.dumps(answer, ensure_ascii=False, separators=(",", ":"))[len('{"date":"2026-11-01",'):-1]
            + ",source:report})}")
    start = source.index(" {name:'simplicio_benchmark'")
    end = source.index("source:report})}", start) + len("source:report})}")
    path.write_text(source[:start] + tool + source[end:])


def session_rows(model: dict, root: Path) -> list:
    price = replay.load_route(model["id"])[1]
    rows = []
    for key, (folder, _title) in site_bench.TASKS.items():
        path = root / folder / "results.json"
        if not path.exists():
            continue
        for record in json.loads(path.read_text()):
            if not (record.get("create_run") and record.get("session")):
                continue
            tokens = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
            for phase in ("create_phase", "edit_phase"):
                for name, value in ((record.get(phase) or {}).get("tokens") or {}).items():
                    tokens[name] += value
            total = site_bench.total_tokens(record, price)
            rows.append({
                "model": model["id"], "task": key, "condition": record["condition"], "rep": record["rep"],
                "wall_s": round(replay.session_seconds(record), 3), "requests": total["requests"],
                "input_tokens": tokens["input"], "output_tokens": tokens["output"],
                "reasoning_tokens": tokens["reasoning"], "cache_read_tokens": tokens["cache_read"],
                "cache_write_tokens": tokens["cache_write"], "cost_usd": round(total["cost_usd"], 6),
                "delivered": replay.delivered(record),
            })
    return rows


def money(value: float) -> str:
    return f"US$ {value:.4f}"


def result_table(run: dict) -> str:
    lines = ["| Model | Client | Task | Setup | n | Time | Model requests | Output tokens | Cost | Delivered |",
             "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for model in run["models"]:
        first_model = True
        for task in model["tasks"]:
            first_task = True
            for row in task["results"]:
                lines.append(
                    f"| {model['name'] if first_model else ''} | {model['client'] if first_model else ''} "
                    f"| {task['title'] if first_task else ''} | {row['setup']} | {row['n']} | {row['seconds']:.1f} s "
                    f"| {row['requests']:g} | {row['output_tokens']:,} | {money(row['cost_usd'])} "
                    f"| {row['delivered']}/{row['n']} |")
                first_model = first_task = False
    return "\n".join(lines)


def side(task: dict, setup: str) -> dict | None:
    return next((row for row in task["results"] if row["setup"] == setup), None)


def script_lines(run: dict) -> str:
    lines = []
    for model in run["models"]:
        task = next((item for item in model["tasks"] if item["id"] == "script"), None)
        if not task:
            continue
        ours, other = side(task, "Simplicio 3.10.8"), side(task, "No MCP")
        lines.append(f"  - {model['name']}: {ours['seconds']:.1f} s and {money(ours['cost_usd'])} with Simplicio, "
                     f"{other['seconds']:.1f} s and {money(other['cost_usd'])} without.")
    return "\n".join(lines)


def price_lines(run: dict) -> str:
    lines = []
    for model in run["models"]:
        price = model["price_usd_per_million_tokens"]
        lines.append(f"  - {model['name']}: {price['input']:g} input, {price['output']:g} output and reasoning, "
                     f"{price['cache_read']:g} cache read, {price['cache_write']:g} cache write.")
    return "\n".join(lines)


def report(run: dict) -> str:
    return f"""# Simplicio 3.10.8 with four models ({DATE})

A real model creates a file and edits it in the same session, once per run, with and without Simplicio. Four models, three tasks, {run['sessions']} sessions. Per-session data: [{STEM}.json]({STEM}.json).

## Result

Medians. Cost comes from the tokens used at each model's list price, so it does not depend on the plan of the account that ran the session. Output tokens include reasoning.

{result_table(run)}

## What this does not show

- The gain comes from the generator. On the script, no generator covers the task, and no MCP was faster and cheaper on every model:
{script_lines(run)}
- A valid request the closed scope does not recognise takes the slower path. On a frozen set, 10 of 15 valid requests reached the generator, and 15 of 15 invalid requests were refused.
- Each model ran in one client. Compare a model with itself, not one model with another.
- Few sessions: 5 per setup, 3 for Grok 4.7. DeepSeek V4.1 Flash keeps the [2026-10-31 round](2026-10-31-map-codegen.md), with 10 and 6 sessions, and compares with 3.9.2 on the new page, the one task it did not run without MCP.
- These are three small tasks. Other tasks and models will give other numbers.
- GPT, Muse and Qwen are not here. A GPT-6 Luna round and a repeat of the DeepSeek round were discarded: a queue that should have stopped kept running and shared work folders with them. Every session in this report ran with its folder to itself.

## Method

- Simplicio 3.10.8, release binary, sha256 starts with `08cada751c31df6b`. Both setups of a model use the same client, the same model and a new git repository per session.
- Claude Sonnet 5.5 ran in Claude Code 2.1.316, and Grok 4.7 in Grok Build 1.0.46, headless, with no user configuration. Time and tokens come from their session logs.
- Claude Haiku 5.5 and DeepSeek V4.1 Flash ran in OpenCode 2.1.4 through OpenRouter, each on one fixed endpoint. Time and tokens come from the OpenCode session database.
- Time is the wall clock of the two turns of a session.
- List prices per million tokens, in US$:
{price_lines(run)}
- Delivery is checked outside the session, as in the [2026-10-31 report](2026-10-31-map-codegen.md#method). Headless Chrome opens each page and tests rows, search, sort, filter and counter. `stats.py` is executed and its counts are compared with the data. The data file must stay unchanged.
- The prompts are the ones in that report.
- Harness: [harness-2026-11-01](harness-2026-11-01/).
"""


def public_data(run: dict, data: dict) -> dict:
    roots = {model: root for model, _name, root in site_bench.ROUNDS}
    sessions = []
    for model in data["models"]:
        sessions += session_rows(model, roots[model["id"]])
    summary = [{"model": model["id"], "task": task["id"], "setup": row["setup"], "n": row["n"],
                "delivered": row["delivered"], "median_wall_s": row["seconds"], "median_requests": row["requests"],
                "median_output_tokens": row["output_tokens"], "median_cost_usd": row["cost_usd"]}
               for model in run["models"] for task in model["tasks"] for row in task["results"]]
    return {"schema": "simplicio.benchmark/v1", "date": DATE, "simplicio": run["simplicio"], "statistic": "median",
            "models": [{"model": model["id"], "client": model["client"],
                        "price_usd_per_million_tokens": model["price_usd_per_million_tokens"]}
                       for model in run["models"]],
            "summary": summary, "sessions": sessions}


def main() -> int:
    public = Path(sys.argv[1])
    data = json.loads((SITE / "assets/data/simplicio-bench.json").read_text())
    run = entry(data)
    write_dataset(run)
    write_webmcp(run)
    sessions = public_data(run, data)
    assert len(sessions["sessions"]) == run["sessions"], (len(sessions["sessions"]), run["sessions"])
    medians = statistics.median(row["wall_s"] for row in sessions["sessions"])
    (public / "benchmarks" / (STEM + ".md")).write_text(report(run))
    (public / "benchmarks" / (STEM + ".json")).write_text(json.dumps(sessions, ensure_ascii=False, indent=2) + "\n")
    print("sessions", run["sessions"], "models", len(run["models"]), "overall median s", round(medians, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
