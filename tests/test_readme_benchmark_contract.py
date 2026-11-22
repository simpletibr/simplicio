"""The README, the benchmark report, the chart and the public data must agree.

Every number printed in the README and in the report is recomputed here from
`benchmarks/2026-11-22-standard-benchmark.json`. The chart is checked against
the same file. The public texts must also stay free of the phrases that would
explain how the product reaches its result.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
DATA = ROOT / "benchmarks" / "2026-11-22-standard-benchmark.json"
REPORT = ROOT / "benchmarks" / "2026-11-22-standard-benchmark.md"
README = ROOT / "README.md"
CHART_SCRIPT = ROOT / "scripts" / "render_benchmark_chart.py"
SVGS = (
    ROOT / "assets" / "benchmark-2026-11-22-light.svg",
    ROOT / "assets" / "benchmark-2026-11-22-dark.svg",
)

ARM_IDS = ("no-simplicio", "simplicio-3.14.0", "simplicio-3.15.0")

TOP_LEVEL_KEYS = {"schema", "date", "model", "agent", "machine", "arms", "sessions"}
STEP_KEYS = {
    "step", "name", "delivered", "checks", "wall_s", "cpu_s", "peak_rss_mb",
    "input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens",
    "cache_write_tokens", "cost_usd_cli", "cost_usd_table", "model_requests",
    "tool_calls",
}
REMOVED_RAW_KEYS = {
    "sequence", "tool_names", "simplicio_replies", "binary", "stderr",
    "mcp_status", "errors", "usage", "num_turns", "tools", "cost_real",
    "cost_table", "cpu_per_wall", "max_repeat", "capped", "provider_error",
    "group", "version", "check", "phases", "exit",
}

# Built in two pieces, as scripts/repository_policy.py does, so this file does
# not match its own pattern.
PRIVATE_PATH_RE = re.compile(r"(?:/" + r"home/[^/\s]+|/" + r"Users/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")


# --------------------------------------------------------------------------
# Independent recomputation from the public JSON
# --------------------------------------------------------------------------

def _data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _d(value) -> Decimal:
    return Decimal(str(value))


def _round(value: Decimal, places: int) -> str:
    return str(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def _median(values):
    ordered = sorted(values)
    assert len(ordered) % 2 == 1, "the contract assumes an odd number of sessions per setup"
    return ordered[len(ordered) // 2]


def _session_totals(data: dict) -> dict[str, list[dict]]:
    totals: dict[str, list[dict]] = {arm: [] for arm in ARM_IDS}
    for session in data["sessions"]:
        steps = session["steps"]
        totals[session["arm"]].append({
            "wall": sum(_d(s["wall_s"]) for s in steps),
            "cpu": sum(_d(s["cpu_s"]) for s in steps),
            "rss": max(_d(s["peak_rss_mb"]) for s in steps),
            "input": sum(s["input_tokens"] for s in steps),
            "output": sum(s["output_tokens"] for s in steps),
            "cost_cli": sum(_d(s["cost_usd_cli"]) for s in steps),
            "cost_table": sum(_d(s["cost_usd_table"]) for s in steps),
            "requests": sum(s["model_requests"] for s in steps),
            "tools": sum(s["tool_calls"] for s in steps),
            "delivered": sum(1 for s in steps if s["delivered"]),
            "steps": len(steps),
        })
    return totals


def _spread(totals: dict, arm: str, key: str):
    values = [session[key] for session in totals[arm]]
    return _median(values), min(values), max(values)


def _cell(totals: dict, arm: str, key: str) -> str:
    """The text of one table cell: median, then the range, as the README prints it."""
    med, lo, hi = _spread(totals, arm, key)
    if key == "wall":
        return f"{_round(med, 0)} s ({_round(lo, 0)} to {_round(hi, 0)})"
    if key == "cpu":
        return f"{_round(med, 1)} s ({_round(lo, 1)} to {_round(hi, 1)})"
    if key == "rss":
        return f"{_round(med, 0)} MB ({_round(lo, 0)} to {_round(hi, 0)})"
    if key in ("cost_cli", "cost_table"):
        return f"${_round(med, 4)} ({_round(lo, 4)} to {_round(hi, 4)})"
    if key in ("input", "output"):
        return f"{med:,} ({lo:,} to {hi:,})"
    return f"{med} ({lo} to {hi})"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _plain(text: str) -> str:
    """The text a reader sees: entities decoded and non-breaking spaces made plain."""
    return html.unescape(text).replace("\u00a0", " ")


# --------------------------------------------------------------------------
# (b) the public data
# --------------------------------------------------------------------------

def _walk_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _walk_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_keys(item)


def test_public_json_has_exactly_the_three_published_arms():
    data = _data()
    assert data["schema"] == "simplicio.public-benchmark/v1"
    assert set(data) == TOP_LEVEL_KEYS
    assert tuple(data["arms"]) == ARM_IDS
    assert {session["arm"] for session in data["sessions"]} == set(ARM_IDS)
    for arm in ARM_IDS:
        sessions = [s for s in data["sessions"] if s["arm"] == arm]
        assert [s["rep"] for s in sessions] == [1, 2, 3], arm
        for session in sessions:
            assert [step["step"] for step in session["steps"]] == [1, 2, 3]
            for step in session["steps"]:
                assert set(step) == STEP_KEYS


def test_public_json_carries_none_of_the_raw_record_keys():
    data = _data()
    keys = set(_walk_keys(data))
    assert not keys & REMOVED_RAW_KEYS, sorted(keys & REMOVED_RAW_KEYS)


def test_public_files_name_only_published_setups_and_no_private_paths():
    texts = {path: _read(path) for path in (DATA, REPORT, CHART_SCRIPT, *SVGS)}
    email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
    for path, text in texts.items():
        assert not re.search(r"\batual\b", text, re.IGNORECASE), path
        assert not PRIVATE_PATH_RE.search(text), path
        assert not re.search(r"\bpr\d{4,}\b", text, re.IGNORECASE), path
        assert not email.search(text), path
        for private in ("simplicio-runtime", "keepbins", "bench/results"):
            assert private not in text, (path, private)
    # A bare "#1234" is a pull request number; the SVGs and the script use colours such as #008300.
    for path in (DATA, REPORT, README):
        assert not re.search(r"(?<![0-9A-Za-z#&])#\d{4,}\b", _read(path)), path
    readme = _read(README)
    assert not re.search(r"\batual\b", readme, re.IGNORECASE)
    assert not re.search(r"\bpr\d{4,}\b", readme, re.IGNORECASE)
    for private in ("simplicio-runtime", "keepbins", "bench/results"):
        assert private not in readme


# --------------------------------------------------------------------------
# (a) the numbers in the README and in the report
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", [README, REPORT], ids=["README", "report"])
def test_tables_carry_the_medians_and_ranges_recomputed_from_the_json(path):
    text = _read(path)
    totals = _session_totals(_data())
    for arm in ARM_IDS:
        for key in ("wall", "cost_cli", "requests", "tools", "output", "input", "cpu", "rss"):
            cell = _cell(totals, arm, key)
            assert cell in text, f"{path.name}: {arm} {key}: {cell!r} not found"
        delivered = sum(s["delivered"] for s in totals[arm])
        total = sum(s["steps"] for s in totals[arm])
        assert f"{delivered} of {total}" in text
    assert "9 of 9" in text


def test_report_also_carries_the_fixed_price_table_cost_and_the_per_step_table():
    text = _read(REPORT)
    data = _data()
    totals = _session_totals(data)
    for arm in ARM_IDS:
        med = _spread(totals, arm, "cost_table")[0]
        assert f"${_round(med, 4)}" in text, arm
    for step in (1, 2, 3):
        for arm in ARM_IDS:
            walls = [_d(s["steps"][step - 1]["wall_s"]) for s in data["sessions"] if s["arm"] == arm]
            costs = [_d(s["steps"][step - 1]["cost_usd_cli"]) for s in data["sessions"] if s["arm"] == arm]
            cell = f"{_round(_median(walls), 1)} s"
            assert cell in text, (step, arm, cell)
            assert f"${_round(_median(costs), 4)}" in text, (step, arm)


def test_readme_headline_and_reading_paragraph_match_the_data():
    text = _plain(_read(README))
    totals = _session_totals(_data())
    none, prev, new = (_spread(totals, arm, "wall")[0] for arm in ARM_IDS)
    cost_none, cost_new = (_spread(totals, arm, "cost_cli")[0] for arm in (ARM_IDS[0], ARM_IDS[2]))
    assert f"{_round(none, 0)} s → {_round(new, 0)} s" in text
    assert f"${_round(cost_none, 4)} → ${_round(cost_new, 4)}" in text
    assert f"{_round(none / new, 1)} times faster" in text
    assert f"{_round(prev / new, 1)} times faster" in text
    req_none, req_new = (_spread(totals, arm, "requests")[0] for arm in (ARM_IDS[0], ARM_IDS[2]))
    out_none, out_new = (_spread(totals, arm, "output")[0] for arm in (ARM_IDS[0], ARM_IDS[2]))
    assert f"{req_new} requests instead of {req_none}" in text
    assert f"{out_new:,} output tokens instead of {out_none:,}" in text
    sessions = len([s for s in _data()["sessions"] if s["arm"] == ARM_IDS[0]])
    assert f"median of {sessions} sessions" in text.lower()


def test_report_states_the_whole_percentages_of_the_ratios():
    text = _read(REPORT)
    totals = _session_totals(_data())

    def med(arm, key):
        return _d(_spread(totals, arm, key)[0])

    none, prev, new = ARM_IDS
    for key in ("wall", "cost_cli", "output", "requests", "tools", "cpu"):
        less = (1 - med(new, key) / med(none, key)) * 100
        assert f"{_round(less, 0)}%" in text, (key, less)
    more_memory = (med(new, "rss") / med(none, "rss") - 1) * 100
    assert f"{_round(more_memory, 0)}%" in text
    for key in ("wall", "cost_cli"):
        less = (1 - med(new, key) / med(prev, key)) * 100
        assert f"{_round(less, 0)}%" in text, (key, less)
    assert f"{_round(med(none, 'wall') / med(new, 'wall'), 2)} times" in text
    assert f"{_round(med(prev, 'wall') / med(new, 'wall'), 2)} times" in text


def test_every_step_of_every_session_was_delivered_with_every_check_passing():
    data = _data()
    for session in data["sessions"]:
        for step in session["steps"]:
            assert step["delivered"] is True
            assert step["checks"] and all(step["checks"].values())


# --------------------------------------------------------------------------
# (c) the chart
# --------------------------------------------------------------------------

def _chart_module():
    spec = importlib.util.spec_from_file_location("render_benchmark_chart", CHART_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_committed_svgs_are_what_the_chart_script_would_write():
    module = _chart_module()
    stale = module.check()
    assert stale == [], f"stale or missing chart files: {stale}"


def test_chart_script_check_flag_exits_zero_when_current():
    done = subprocess.run(
        [sys.executable, str(CHART_SCRIPT), "--check"],
        capture_output=True, text=True, timeout=60,
    )
    assert done.returncode == 0, done.stdout + done.stderr


def test_chart_svgs_are_self_contained_and_accessible():
    for path in SVGS:
        text = _read(path)
        assert text.startswith("<svg"), path
        assert 'viewBox="0 0 840 ' in text and 'width="840"' in text, path
        assert "<title" in text and "<desc" in text, path
        for forbidden in ("@import", "url(http", "<image", "<script", "xlink:href"):
            assert forbidden not in text, (path, forbidden)
        totals = _session_totals(_data())
        for arm in ARM_IDS:
            wall = _round(_spread(totals, arm, "wall")[0], 0)
            assert f"{wall} s" in text, (path, arm)


# --------------------------------------------------------------------------
# (d) nothing that explains the mechanism
# --------------------------------------------------------------------------

# Case-insensitive regular expressions. Each one is a phrase that would say or
# hint HOW Simplicio reaches its result, or a claim the repository cannot back.
FORBIDDEN_PHRASES = (
    # the explanation of the gain
    r"generators?\b", r"code[- ]generation", r"codegen", r"writes? the file", r"\b0 llm tokens\b",
    r"zero llm tokens", r"zero[- ]token", r"\b0 tokens\b",
    r"\bhooks?\b", r"pre-?fill", r"prompt[- ]?exec", r"session-start", r"appends? the map",
    r"contract fill", r"\bfill route\b",
    r"\brout(?:e|es|ed|ing)\b",
    r"order gate", r"write order", r"orientation gate", r"orientation_required", r"context_required",
    r"codegen_required", r"\brefusals?\b", r"refusal codes?",
    r"\bthresholds?\b", r"neutral files?", r"\btoon\b", r"reply formats?",
    r"gain comes from", r"the gain\b.{0,40}\bcomes? from", r"secret recipe",
    # internal names
    r"st_prompt_budget", r"cpuexecutor", r"write_workers", r"\btokio\b", r"dag partitioner",
    r"facade", r"simplicio_mcp_profile", r"mapper-only",
    # anything that turns sign-in off
    r"no_login", r"skip_login", r"dev_no_login",
    # claims the repository does not back
    r"never leaves your machine", r"zero (?:silent )?telemetry", r"works offline", r"offline-first",
    r"100% rust", r"~?46\s?mb\b", r"cold start", r"http/oauth",
    # placeholders that must not reach a public page
    r"unverified", r"\btodo\b", r"\btbd\b",
)

# Public names and commands that the forbidden list must never catch.
ALLOWED_PUBLIC_STRINGS = (
    "simplicio_context", "simplicio_map", "simplicio_edit", "simplicio_validate", "simplicio_run",
    "simplicio map --repo . --for-llm markdown", "simplicio context --repo .",
    'simplicio memory query "query" --json', "simplicio edit --plan plan.json --repo .",
    'simplicio run "task" --repo . --agents N', "simplicio loop", "simplicio onboard", "simplicio version",
    "simplicio mcp register", "simplicio serve --mcp --stdio", "simplicio auth login",
    "Mapper observes, Fast projects or retrieves, Dev CLI edits, Runtime governs, and Loop converges.",
    "local STDIO MCP", "SIMPLICIO_CONFIRM_PURGE=1", "--uninstall --keep-data", "--uninstall --purge",
)


def test_forbidden_list_does_not_catch_the_public_interface():
    for phrase in ALLOWED_PUBLIC_STRINGS:
        for pattern in FORBIDDEN_PHRASES:
            assert not re.search(pattern, phrase, re.IGNORECASE), (pattern, phrase)


@pytest.mark.parametrize("path", [README, REPORT, DATA, *SVGS, CHART_SCRIPT], ids=lambda p: p.name)
def test_public_benchmark_texts_do_not_explain_the_mechanism(path):
    text = _read(path)
    hits = [pattern for pattern in FORBIDDEN_PHRASES if re.search(pattern, text, re.IGNORECASE)]
    assert not hits, f"{path.name} matches forbidden patterns: {hits}"


def test_readme_does_not_use_the_retired_hero_images():
    text = _read(README)
    assert "simplicio-hero" not in text


def test_readme_keeps_the_phrases_other_contracts_pin():
    text = _read(README)
    for needle in ("local STDIO MCP", "serve --mcp --stdio", "Mapper observes", "automatically",
                   "simplicio_context", "docs/flow/simplicio.svg"):
        assert needle in text, needle
    assert "HTTP/OAuth" not in text
    assert "Authenticate" not in text
