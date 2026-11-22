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
import struct
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

# The brand line: the same English text in every language, never translated.
TAGLINE = "<p><b>UltraFast Mode for all.</b></p>"
LOCALIZED = sorted((ROOT / "READMEs").glob("README.*.md"))

TOP_LEVEL_KEYS = {"schema", "date", "model", "agent", "machine", "round", "arms", "sessions"}
SESSION_KEYS = {"arm", "rep", "steps", "totals"}
# Per step: delivery, checks, time, CPU, memory and cost. Counts are published per session, not per step.
STEP_KEYS = {"step", "name", "delivered", "checks", "wall_s", "cpu_s", "peak_rss_mb", "cost_usd_cli"}
TOTALS_KEYS = {
    "input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens",
    "model_requests", "tool_calls", "cost_usd_table",
}
PER_STEP_COUNT_KEYS = TOTALS_KEYS - {"cost_usd_table"} | {"cost_usd_table"}
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
            "input": session["totals"]["input_tokens"],
            "output": session["totals"]["output_tokens"],
            "reasoning": session["totals"]["reasoning_tokens"],
            "cache_read": session["totals"]["cache_read_tokens"],
            "cost_cli": sum(_d(s["cost_usd_cli"]) for s in steps),
            "cost_table": _d(session["totals"]["cost_usd_table"]),
            "requests": session["totals"]["model_requests"],
            "tools": session["totals"]["tool_calls"],
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
    if key in ("input", "output", "reasoning", "cache_read"):
        return f"{med:,} ({lo:,} to {hi:,})"
    return f"{med} ({lo} to {hi})"


def _readme_cell_parts(totals: dict, arm: str, key: str) -> tuple[str, str]:
    """The value and the range as the README prints them: the range sits under the value."""
    med, lo, hi = _spread(totals, arm, key)
    if key == "wall":
        return f"{_round(med, 0)} s", f"{_round(lo, 0)}\u2013{_round(hi, 0)}"
    if key == "cpu":
        return f"{_round(med, 1)} s", f"{_round(lo, 1)}\u2013{_round(hi, 1)}"
    if key == "rss":
        return f"{_round(med, 0)} MB", f"{_round(lo, 0)}\u2013{_round(hi, 0)}"
    if key == "cost_cli":
        return f"${_round(med, 4)}", f"{_round(lo, 4)}\u2013{_round(hi, 4)}"
    if key in ("input", "output", "reasoning", "cache_read"):
        return f"{med:,}", f"{lo:,}\u2013{hi:,}"
    return f"{med}", f"{lo}\u2013{hi}"


def _best_arm_with_a_clear_gap(totals: dict, key: str):
    """The arm with the lowest median, or None when its range overlaps another arm's range."""
    spreads = {arm: _spread(totals, arm, key) for arm in ARM_IDS}
    best = min(ARM_IDS, key=lambda arm: spreads[arm][0])
    _, lo, hi = spreads[best]
    for arm, (_, other_lo, other_hi) in spreads.items():
        if arm != best and other_lo <= hi and lo <= other_hi:
            return None
    return best


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
            assert set(session) == SESSION_KEYS
            assert set(session["totals"]) == TOTALS_KEYS
            assert [step["step"] for step in session["steps"]] == [1, 2, 3]
            for step in session["steps"]:
                assert set(step) == STEP_KEYS


def test_public_json_says_how_many_sessions_the_round_ran_and_why_nine_are_published():
    data = _data()
    round_ = data["round"]
    assert set(round_) == {"sessions_run", "sessions_published", "note"}
    assert round_["sessions_run"] == 12
    assert round_["sessions_published"] == len(data["sessions"]) == 9
    note = round_["note"]
    assert "unreleased development build" in note
    assert "12 sessions" in note and "9" in note and "other 3" in note
    # The fourth setup gets no name, no number and no description beyond this.
    assert len(note.split()) < 50


def test_report_discloses_the_fourth_setup_in_the_setup_table_and_in_the_limits():
    text = _read(REPORT)
    assert text.count("unreleased development build") >= 2
    setup_row = next(line for line in text.splitlines() if line.startswith("| Concurrency |"))
    assert "12 sessions" in setup_row and "9 are reported" in setup_row
    assert "unreleased development build" in setup_row
    assert "is the reason four sessions ran at once" in setup_row
    limits = text.split("## Limits", 1)[1].split("## Data", 1)[0]
    assert "12 sessions, 9 reported" in limits and "unreleased development build" in limits
    assert "is the reason four sessions ran at once" in limits
    assert "`round`" in text.split("## Data", 1)[1]


def test_report_says_counts_are_per_session_and_lists_the_totals_fields():
    report = _read(REPORT)
    assert "Token, request and tool-call counts are published per session, not per step." in report
    data_section = report.split("## Data", 1)[1]
    for key in TOTALS_KEYS:
        assert f"`{key}`" in data_section, key
    step_table = data_section.split("Fields of each step:", 1)[1].split("Token, request and tool-call counts", 1)[0]
    for key in TOTALS_KEYS - {"cost_usd_cli"}:
        assert f"`{key}`" not in step_table, f"{key} is documented as a per-step field"
    assert "in all 27 measured steps" not in report and "in all 9 sessions that count is at or below the output count" in report


def test_public_json_carries_none_of_the_raw_record_keys():
    data = _data()
    keys = set(_walk_keys(data))
    assert not keys & REMOVED_RAW_KEYS, sorted(keys & REMOVED_RAW_KEYS)


def test_public_files_name_only_published_setups_and_no_private_paths():
    texts = {path: _read(path) for path in (DATA, REPORT, CHART_SCRIPT, *FIGURE_FILES)}
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

def test_readme_table_puts_the_value_first_and_the_range_under_it():
    text = _read(README)
    totals = _session_totals(_data())
    assert "The small line under each value is the lowest and the highest session." in text
    for key in ("wall", "cost_cli", "requests", "tools", "output", "input", "cpu", "rss"):
        best = _best_arm_with_a_clear_gap(totals, key)
        for arm in ARM_IDS:
            value, span = _readme_cell_parts(totals, arm, key)
            bold = arm == best
            shown = f"**{value}**" if bold else value
            cell = f"{shown}<br><sub>{span}</sub>"
            assert cell in text, f"README: {arm} {key}: {cell!r} not found"
            if not bold:
                assert f"**{value}**<br><sub>{span}</sub>" not in text, f"README: {arm} {key} must not be bold"
    for arm in ARM_IDS:
        delivered = sum(s["delivered"] for s in totals[arm])
        total = sum(s["steps"] for s in totals[arm])
        assert f"{delivered} of {total}" in text
    assert "| Steps delivered | 9 of 9 | 9 of 9 | 9 of 9 |" in text
    assert " to " not in " ".join(line for line in text.splitlines() if "<sub>" in line and line.startswith("|"))


REPORT_ROWS = ("wall", "cost_cli", "cost_table", "output", "reasoning", "input", "cache_read",
               "requests", "tools", "cpu", "rss")


def test_report_tables_carry_the_medians_and_ranges_with_to():
    text = _read(REPORT)
    totals = _session_totals(_data())
    for arm in ARM_IDS:
        for key in REPORT_ROWS:
            cell = _cell(totals, arm, key)
            assert cell in text, f"report: {arm} {key}: {cell!r} not found"
        delivered = sum(s["delivered"] for s in totals[arm])
        total = sum(s["steps"] for s in totals[arm])
        assert f"{delivered} of {total}" in text
    assert "9 of 9" in text


def test_report_applies_the_bold_rule_to_every_row_the_same_way():
    """Bold marks the lowest median, only where its range does not overlap the other two."""
    text = _read(REPORT)
    totals = _session_totals(_data())
    for key in REPORT_ROWS:
        best = _best_arm_with_a_clear_gap(totals, key)
        for arm in ARM_IDS:
            cell = _cell(totals, arm, key)
            if arm == best:
                assert f"**{cell}**" in text, f"report: {key}: {arm} should be bold"
            else:
                assert f"**{cell}**" not in text, f"report: {key}: {arm} must not be bold"
    assert "The same holds for reasoning tokens" not in text


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
    assert "The ratios come from the unrounded medians." in text
    assert "and the job passed the same outside checks" in text
    assert "for the same delivered result" not in text
    walls = {arm: [s["wall"] for s in totals[arm]] for arm in ARM_IDS}
    costs = {arm: [s["cost_cli"] for s in totals[arm]] for arm in ARM_IDS}
    fastest_none, slowest_new = min(walls[ARM_IDS[0]]), max(walls[ARM_IDS[2]])
    cheapest_none, dearest_new = min(costs[ARM_IDS[0]]), max(costs[ARM_IDS[2]])
    worst = (
        f"Worst case: the fastest session without Simplicio ({_round(fastest_none, 1)} s) was still "
        f"{_round(fastest_none / slowest_new, 1)} times slower than the slowest session with Simplicio 3.15.0 "
        f"({_round(slowest_new, 1)} s), and the cheapest session without it (${_round(cheapest_none, 4)}) still cost "
        f"{_round(cheapest_none / dearest_new, 1)} times as much as the most expensive session with it "
        f"(${_round(dearest_new, 4)})."
    )
    assert worst in text
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


def _registry():
    """(figure, theme, absolute path) for every file the chart script writes: its own registry is the one list."""
    module = _chart_module()
    return [
        (figure, theme, ROOT / module.figure_path(figure, theme))
        for figure in module.FIGURES
        for theme in module.THEME_NAMES
    ]


FIGURE_FILES = [path for _, _, path in _registry()]


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
        # The annotations on the Simplicio 3.15.0 rows, against no Simplicio.
        none, new = ARM_IDS[0], ARM_IDS[2]

        def med(arm, key):
            return _d(_spread(totals, arm, key)[0])

        faster = f"{_round(med(none, 'wall') / med(new, 'wall'), 1)}\u00d7 faster"
        less = f"{_round((1 - med(new, 'cost_cli') / med(none, 'cost_cli')) * 100, 0)}% less"
        fewer = f"{_round((1 - med(new, 'output') / med(none, 'output')) * 100, 0)}% fewer"
        for note in (faster, less, fewer):
            assert f">{note}</tspan>" in text, (path.name, note)
            assert note in text.split("<desc", 1)[1].split("</desc>", 1)[0], (path.name, note, "desc")


# --------------------------------------------------------------------------
# the figures: one registry, every file current, referenced and truthful
# --------------------------------------------------------------------------

PICTURE_RE = re.compile(
    r'<picture>\s*<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)">\s*'
    r'<img src="([^"]+)" width="840" alt="([^"]*)">\s*</picture>'
)


def _pictures(text: str) -> list[tuple[str, str, str]]:
    return [(m.group(1), m.group(2), html.unescape(m.group(3))) for m in PICTURE_RE.finditer(text)]


def _desc(path: Path) -> str:
    match = re.search(r'<desc id="desc">(.*?)</desc>', _read(path), re.DOTALL)
    assert match, f"{path.name}: no <desc>"
    return html.unescape(match.group(1))


def _arm_labels() -> dict[str, str]:
    return {arm: info["label"] for arm, info in _data()["arms"].items()}


def _step_median(arm: str, step: int) -> Decimal:
    values = [_d(s["steps"][step - 1]["wall_s"]) for s in _data()["sessions"] if s["arm"] == arm]
    return _median(values)


def _session_pairs(totals: dict, arm: str) -> list[tuple[Decimal, Decimal]]:
    return sorted((record["wall"], record["cost_cli"]) for record in totals[arm])


def _expected_figure_numbers() -> dict[str, dict[str, list[str]]]:
    """For every figure key: strings that must be in its <desc>, and strings that must be in the README alt text."""
    totals = _session_totals(_data())
    labels = _arm_labels()
    none, prev, new = ARM_IDS

    def med(arm, key):
        return _d(_spread(totals, arm, key)[0])

    out: dict[str, dict[str, list[str]]] = {}

    # the headline chart
    faster = f"{_round(med(none, 'wall') / med(new, 'wall'), 1)}× faster"
    less = f"{_round((1 - med(new, 'cost_cli') / med(none, 'cost_cli')) * 100, 0)}% less"
    fewer = f"{_round((1 - med(new, 'output') / med(none, 'output')) * 100, 0)}% fewer"
    walls = [f"{_round(med(arm, 'wall'), 0)} s" for arm in ARM_IDS]
    costs = [f"${_round(med(arm, 'cost_cli'), 4)}" for arm in ARM_IDS]
    tokens = [f"{int(med(arm, 'output')):,}" for arm in ARM_IDS]
    out["hero"] = {
        "desc": [f"{labels[a]} {w}" for a, w in zip(ARM_IDS, walls)]
        + [f"{labels[a]} {c}" for a, c in zip(ARM_IDS, costs)]
        + [f"{labels[a]} {t}" for a, t in zip(ARM_IDS, tokens)]
        + [faster, less, fewer],
        "alt": [
            f"{walls[0]} with no Simplicio, {walls[1]} with Simplicio 3.14.0 and {walls[2]} with Simplicio 3.15.0",
            f"Cost: {costs[0]}, {costs[1]} and {costs[2]}",
            f"Output tokens: {tokens[0]}, {tokens[1]} and {tokens[2]}",
        ],
    }

    # every session
    desc, alt = [], []
    for arm in ARM_IDS:
        pairs = _session_pairs(totals, arm)
        assert len(pairs) == 3
        desc += [f"{_round(w, 0)} s and ${_round(c, 4)}" for w, c in pairs]
        lo_w, hi_w = pairs[0][0], pairs[-1][0]
        costs_sorted = sorted(c for _, c in pairs)
        alt.append(f"{_round(lo_w, 0)} to {_round(hi_w, 0)} s and "
                   f"${_round(costs_sorted[0], 4)} to ${_round(costs_sorted[-1], 4)}")
    out["sessions"] = {"desc": desc, "alt": alt}

    # requests and tool calls
    counts = {key: [int(med(arm, key)) for arm in ARM_IDS] for key in ("requests", "tools")}
    out["work"] = {
        "desc": [f"{labels[arm]} {counts[key][i]}" for key in counts for i, arm in enumerate(ARM_IDS)],
        "alt": [
            f"Model requests: {counts['requests'][0]} with no Simplicio, {counts['requests'][1]} with Simplicio 3.14.0 "
            f"and {counts['requests'][2]} with Simplicio 3.15.0",
            f"Tool calls: {counts['tools'][0]}, {counts['tools'][1]} and {counts['tools'][2]}",
        ],
    }

    # time by step
    steps = {step: [_round(_step_median(arm, step), 1) for arm in ARM_IDS] for step in (1, 2, 3)}
    out["steps"] = {
        "desc": [f"{labels[arm]} {steps[step][i]} s" for step in steps for i, arm in enumerate(ARM_IDS)],
        "alt": [
            f"Step 1, build: {steps[1][0]} s with no Simplicio, {steps[1][1]} s with Simplicio 3.14.0 "
            f"and {steps[1][2]} s with Simplicio 3.15.0",
            f"Step 2, change: {steps[2][0]} s, {steps[2][1]} s and {steps[2][2]} s",
            f"Step 3, register: {steps[3][0]} s, {steps[3][1]} s and {steps[3][2]} s",
        ],
    }

    # peak memory: the loss, in numbers
    rss = [_round(med(arm, "rss"), 0) for arm in ARM_IDS]
    more_prev = f"{_round((med(prev, 'rss') / med(none, 'rss') - 1) * 100, 0)}% more"
    more_new = f"{_round((med(new, 'rss') / med(none, 'rss') - 1) * 100, 0)}% more"
    out["memory"] = {
        "desc": [f"{labels[arm]} {rss[i]} MB" for i, arm in enumerate(ARM_IDS)] + [more_prev, more_new],
        "alt": [
            f"{rss[0]} MB with no Simplicio, the lowest",
            f"{rss[1]} MB with Simplicio 3.14.0, {more_prev}",
            f"{rss[2]} MB with Simplicio 3.15.0, {more_new}",
        ],
    }
    return out


def test_registry_lists_every_figure_the_script_writes_and_every_file_is_current():
    module = _chart_module()
    keys = [figure.key for figure in module.FIGURES]
    assert keys == ["hero", "sessions", "work", "steps", "memory"]
    files = [path for _, _, path in _registry()]
    assert len(files) == len(set(files)) == 2 * len(keys)
    for path in files:
        assert path.is_file(), f"{path.name} is missing"
    assert module.check() == [], "stale or missing figure files: run python3 scripts/render_benchmark_chart.py"


@pytest.mark.parametrize("path", FIGURE_FILES, ids=lambda p: p.name)
def test_every_figure_is_self_contained_and_accessible(path):
    text = _read(path)
    assert text.startswith("<svg"), path.name
    assert 'viewBox="0 0 840 ' in text and 'width="840"' in text, path.name
    assert 'role="img"' in text and "<title" in text and "<desc" in text, path.name
    for forbidden in ("@import", "url(http", "<image", "<script", "xlink:href", "href=", "<foreignObject"):
        assert forbidden not in text, (path.name, forbidden)
    sizes = [float(size) for size in re.findall(r"font-size:(\d+(?:\.\d+)?)px", text)]
    assert sizes and min(sizes) >= 19, (path.name, sizes)


def test_every_figure_desc_carries_the_numbers_recomputed_from_the_json():
    expected = _expected_figure_numbers()
    for figure, theme, path in _registry():
        desc = _desc(path)
        for needle in expected[figure.key]["desc"]:
            assert needle in desc, f"{path.name}: {needle!r} not in <desc>"


def test_readme_references_every_figure_through_a_picture_with_a_dark_source_and_a_light_default():
    pictures = _pictures(_read(README))
    by_light = {light: (dark, alt) for dark, light, alt in pictures}
    assert len(by_light) == len(pictures), "a figure is placed twice"
    for figure, _theme, _path in _registry():
        light = f"assets/{figure.stem}-light.svg"
        assert light in by_light, f"README does not show {light}"
        assert by_light[light][0] == f"assets/{figure.stem}-dark.svg", figure.key


def test_readme_alt_texts_state_the_numbers_of_their_figures():
    expected = _expected_figure_numbers()
    by_light = {light: alt for _dark, light, alt in _pictures(_read(README))}
    for figure, _theme, _path in _registry():
        alt = by_light[f"assets/{figure.stem}-light.svg"]
        for needle in expected[figure.key]["alt"]:
            assert needle in alt, f"README alt of {figure.key}: {needle!r} not found in {alt!r}"


def test_every_image_the_readme_and_the_report_show_exists_in_the_repository():
    for path in (README, REPORT):
        text = _read(path)
        targets = re.findall(r'(?:src|srcset)="([^"]+)"', text) + re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text)
        assert targets, path.name
        for target in targets:
            if target.startswith(("http://", "https://", "data:")):
                continue
            assert (path.parent / target).resolve().is_file(), f"{path.name} shows {target}, which does not exist"


def test_report_shows_the_sessions_steps_and_memory_figures_next_to_their_tables():
    text = _read(REPORT)
    by_light = {light: (dark, alt) for dark, light, alt in _pictures(text)}
    expected = _expected_figure_numbers()
    module = _chart_module()
    for figure in module.FIGURES:
        light = f"../assets/{figure.stem}-light.svg"
        if figure.key in ("sessions", "steps", "memory"):
            assert light in by_light, f"report does not show {light}"
            assert by_light[light][0] == f"../assets/{figure.stem}-dark.svg"
            for needle in expected[figure.key]["alt"]:
                assert needle in by_light[light][1], (figure.key, needle)
        else:
            assert light not in by_light, figure.key
    # next to the tables they picture
    assert text.index("sessions-light.svg") < text.index("### By step")
    assert text.index("### By step") < text.index("steps-light.svg") < text.index("Median time of each step")
    assert text.index("## Where Simplicio did not win") < text.index("memory-light.svg") < text.index("- **Memory.**")


def test_readme_puts_each_figure_where_the_page_needs_it_and_keeps_the_exact_numbers_visible():
    text = _read(README)

    def at(needle):
        return text.index(needle)

    assert at("Every session is on this chart, not only the medians.") < at("sessions-light.svg") < at("| Measure | No Simplicio")
    assert at("| Steps delivered | 9 of 9 |") < at("What changed in the session, in counts") < at("work-light.svg")
    assert at("work-light.svg") < at("Time by step, on one shared scale.") < at("steps-light.svg")
    details = "<details>\n<summary>Exact numbers by step</summary>"
    assert at("steps-light.svg") < at(details) < at("| 1. Build | 57.3 s")
    # the by-step table is inside the details block, not visible on its own
    before = text[: at(details)]
    assert "| 1. Build |" not in before
    assert at("| 3. Register |") < at("</details>", ) < at("**How to read it.**")
    assert at("### Where Simplicio does not win") < at("memory-light.svg") < at("- **Memory.**")
    assert "| Measure | No Simplicio | Simplicio 3.14.0 | Simplicio 3.15.0 |" in text


def test_privacy_section_lists_the_destinations_and_does_not_claim_only_what_you_configure():
    text = _read(README)
    section = text.split("## Safety and privacy", 1)[1].split("## Also in this repository", 1)[0]
    assert "This section describes version 3.15.0." in section
    for needle in ("**Stays on your machine.**", "**To SimpleTI (simpleti.com.br).**", "**To GitHub.**",
                   "**No analytics.**", "**To services you configure.**",
                   "**Two features reach a public service without any configuration.**", "**Downloads.**",
                   "DuckDuckGo", "osv.dev", "SIMPLICIO_DISABLE_AUTO_UPDATE=1"):
        assert needle in section, needle
    assert "only when you point Simplicio at one yourself" not in text
    assert "**Signed releases.**" in section and "**What the installer changes in your agent.**" in section


# --------------------------------------------------------------------------
# what the page says about agents, checks, links, install and wording
# --------------------------------------------------------------------------

HOSTS_MATRIX = ROOT / "docs" / "hosts" / "compatibility-matrix.md"
HOST_REGISTRY = ROOT / "plugins" / "simplicio" / "host-surfaces.json"


def _matrix_rows() -> dict[str, str]:
    """Agent name to its capability, read from the compatibility matrix."""
    rows = {}
    for line in _read(HOSTS_MATRIX).splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] != "Host" and not set(cells[0]) <= {"-", " "}:
            rows[cells[0]] = cells[1]
    return rows


def _section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


SURFACE_GROUPS = (
    ("An MCP entry that Simplicio writes", ("runtime-mcp",)),
    ("A native plugin or extension", ("native-plugin", "native-extension")),
    ("A portable plugin package", ("agent-plugin-v1",)),
    ("A guided setup you follow yourself", ("guided-runtime",)),
    ("Another command-line tool", ("delegated-cli",)),
)
SEVEN_NAMED_AGENTS = ("Claude Code", "Codex", "Cursor", "Visual Studio Code", "OpenCode", "Gemini CLI", "Kiro")


def _registry_hosts() -> list[dict]:
    return json.loads(_read(HOST_REGISTRY))["hosts"]


def _lower_first(text: str) -> str:
    return text[0].lower() + text[1:]


def _guides_for_registry_agents(registry: list[dict]) -> list[str]:
    """Registry ids that have a guide page. pi.md covers Pi and oh-my-pi, orca.md covers OrcaDev / Orca ADE."""
    stems = {path.stem for path in (ROOT / "docs" / "hosts").glob("*.md") if path.stem != "compatibility-matrix"}
    alias = {"orca-dev": "orca", "oh-my-pi": "pi"}
    return [host["id"] for host in registry if host["id"] in stems or alias.get(host["id"]) in stems]


def test_agents_section_is_written_from_the_registry_and_the_matrix():
    text = _read(README)
    section = _section(text, "## Works with the agent you already use", "<summary>Manual configuration</summary>")
    registry = _registry_hosts()
    names = [host["name"] for host in registry]
    matrix = _matrix_rows()
    supported = [name for name, capability in matrix.items() if capability != "unsupported"]
    assert all(name in names for name in supported)
    lower_rows = [row.lower() for row in matrix]
    unverified = [n for n in names if n not in supported and any(n.lower() in row for row in lower_rows)]
    no_row = [n for n in names if n not in supported and n not in unverified]

    # how Simplicio reaches each agent: the registry's surface field
    counts = [(label, sum(1 for host in registry if host["surface"] in surfaces)) for label, surfaces in SURFACE_GROUPS]
    assert sum(n for _, n in counts) == len(names), "a registry surface is not in any group of the table"
    parts = [f"{_lower_first(label)} ({n})" for label, n in counts]
    reaches = ", ".join(parts[:-1]) + f", or {parts[-1]}"
    assert f"names {len(names)} agent ids and says, for each, how Simplicio reaches it: {reaches}." in section

    # what has been verified: the matrix
    assert len(supported) + len(unverified) + len(no_row) == len(names)
    assert (f"Of those {len(names)} it marks {len(supported)} agents as supported and {len(unverified)} `unverified`, "
            f"and it has no row for {' and '.join(no_row)}.") in section
    assert ("Where the registry says Simplicio writes the entry and the matrix says `unverified`, "
            "treat that integration as untested.") in section

    # the seven agents named as examples exist in the registry and in the sentence
    sentence = "among them " + ", ".join(SEVEN_NAMED_AGENTS[:-1]) + " and " + SEVEN_NAMED_AGENTS[-1] + "."
    assert sentence in section
    for name in SEVEN_NAMED_AGENTS:
        assert name in names, name
    assert "The installer hands registration to Simplicio's own registrar." in section

    # guides and plugins
    assert f"{len(_guides_for_registry_agents(registry))} agents have a guide in [`docs/hosts/`](docs/hosts/)." in section
    assert ("the plugin is applied in a separate step that asks for your consent, "
            "and [INSTALL.md](INSTALL.md) describes it.") in section

    # the collapsed table: names from the registry, counts in a column, the supported ones in bold
    details = section.split("<details>", 1)[1].split("</details>", 1)[0]
    assert f"<summary>All {len(names)} agents, by how Simplicio reaches them</summary>" in details
    assert "| How Simplicio reaches it | Count | Agents |" in details
    for (label, surfaces), (_, n) in zip(SURFACE_GROUPS, counts):
        members = [host["name"] for host in registry if host["surface"] in surfaces]
        shown = ", ".join(f"**{name}**" if name in supported else name for name in members)
        assert f"| {label} | {n} | {shown} |" in details, label
    assert sorted(re.findall(r"\*\*([^*]+)\*\*", details.split("Bold:", 1)[0])) == sorted(supported)
    assert "Bold: the compatibility matrix marks the agent as supported." in details

    # what must not come back
    for gone in ("nothing is configured automatically", "The installer detects these today",
                 "The other 31 agents in the registry", "If your agent is not one of the 12 above",
                 "| How Simplicio reaches it |\n|---|---|\n| Native plugin or extension (5)",
                 "Each host guide states", "shows what the installer does for each host"):
        assert gone not in text, gone
    assert "If your agent was not configured for you, add this entry to its MCP configuration." in text


def test_readme_says_what_the_checks_do_not_test_and_what_is_published():
    text = _read(README)
    assert ("The checks do not test the search box, sorting, the redirect after saving, "
            "the look of the page or the quality of the code.") in text
    assert text.count("The checks do not test") == 1
    assert ("[The report](benchmarks/2026-11-22-standard-benchmark.md) publishes the three prompts "
            "(in Portuguese, with a translation), a description of every outside check and the per-session numbers") in text
    assert "The test harness is not published." in text
    assert "Each median is taken separately, so the steps do not add up to the whole-job median." in text
    for needle in ("**The previous release showed no gain on this job.**",
                   "**What you install is not exactly what was measured.**",
                   "No session of these three setups was dropped or re-run.",
                   "We have not measured how much of your work looks like this job.",
                   "Read with it: one small job, three sessions per setup, one model."):
        assert needle in text, needle
    assert "pay for itself" not in text


def test_readme_links_no_benchmarks_folder_and_the_report_names_the_old_round_in_code_font():
    readme, report = _read(README), _read(REPORT)
    assert not re.search(r'\]\(benchmarks/?\)|href="benchmarks/?"', readme)
    assert "[`benchmarks/`]" not in readme and "[benchmarks/]" not in readme
    assert "(benchmarks/2026-11-22-standard-benchmark.md)" in readme
    assert "(benchmarks/2026-11-22-standard-benchmark.json)" in readme
    assert "](2026-11-01-multi-model.md)" not in report
    assert "`2026-11-01-multi-model.md`" in report


def test_install_and_safety_statements_match_what_the_scripts_do():
    text = _read(README)
    for needle in ("- `--doctor` checks the installation.",
                   "A purge needs `SIMPLICIO_CONFIRM_PURGE=1`.",
                   "You can run either installer again at any time",
                   "Uninstall does not edit your agents' configuration. The Simplicio entries stay in each agent "
                   "until you remove them in that agent's own settings.",
                   "It does not edit your agents' configuration, so remove the Simplicio entries in each agent's own settings.",
                   "For stable releases the contract makes a missing or invalid signature and a checksum mismatch hard failures.",
                   "The DMG has no signature file and bundles the Simplicio 3.8.47 binary.",
                   "and Gatekeeper acceptance is not claimed, so macOS may warn you when you open it.",
                   "[MCP-CONNECT.md](MCP-CONNECT.md) describes the core tools.",
                   "The commands and tools documented in README.md and MCP-CONNECT.md are drawn as one flow,"):
        assert needle in text, needle
    for gone in ("read-only", "idempotent", "type `PURGE`", "Uninstall removes only the entries", "the full catalogue",
                 "every public command"):
        assert gone not in text, gone
    assert "Windows Desktop is not published." in text and "Apple Developer ID signing" in text


def test_tagline_is_the_same_english_line_in_all_15_pages_under_the_name():
    pages = [README, *LOCALIZED]
    assert len(pages) == 15
    for page in pages:
        text = _read(page)
        assert text.count(TAGLINE) == 1, f"{page.name}: the tagline must appear once, unchanged and in English"
        assert text.count("UltraFast") == 1, f"{page.name}: UltraFast appears outside the tagline"
        lines = text.split("\n")
        index = lines.index(TAGLINE)
        assert lines[index - 2] == "<h1>Simplicio</h1>" and lines[index - 1] == "", \
            f"{page.name}: the tagline goes right under <h1>Simplicio</h1>"
        assert "→" in lines[index + 2] and lines[index + 2].startswith("<p><b>"), \
            f"{page.name}: the measured headline follows the tagline"
        # the two measured expressions keep their right arrows; in the Arabic and Hebrew pages each is one left-to-right unit
        spans = lines[index + 2].count('<span dir="ltr">')
        assert spans == (2 if page.name.endswith(("ar-SA.md", "he-IL.md")) else 0), \
            f"{page.name}: the headline wraps its two expressions in a left-to-right span in ar-SA and he-IL only"


def test_first_screen_questions_and_wording_follow_the_review():
    text = _read(README)
    top = text.split("</div>", 1)[0]
    assert "<b>Same agent, same model, same job: 121&nbsp;s&nbsp;→&nbsp;25&nbsp;s, and $0.0226&nbsp;→&nbsp;$0.0076.</b>" in top
    assert ("<p>Without Simplicio → with Simplicio 3.15.0. Median of 3 runs of one small coding job "
            "in Claude Code with Claude Haiku 5.5.</p>") in top
    assert "<p>Simplicio runs on your machine and adds tools to the coding agent you already use.</p>" in top
    assert top.index("<h1>Simplicio</h1>") < top.index(TAGLINE) < top.index("<b>Same agent, same model, same job:")
    assert text.count(TAGLINE) == 1
    assert ("Simplicio is a local program that gives the coding agent you already use an ultra-fast mode, "
            "whatever the agent and whatever the model. The numbers on this page come from one agent and one model; "
            "the section below says exactly what was measured.") in text
    assert ('<p align="center">How Simplicio gets this result is not published. '
            'The measurements are, including the ones where it loses.</p>') in text
    assert "\n> " not in text
    assert ("Read with it: one small job, three sessions per setup, one model. The outside checks are narrower than the prompts. "
            "Peak memory was higher: 375 MB against 270 MB. The Simplicio builds were compiled from the release commits, "
            "with sign-in off.") in text
    # "setup" is defined where it is first used
    first_use = re.search(r"\bsetups?\b", text).start()
    caption = "Median of 3 sessions for each setup (no Simplicio, Simplicio 3.14.0 and Simplicio 3.15.0)"
    assert first_use == text.index(caption) + len("Median of 3 sessions for each ")
    assert (text.index("## Questions people ask") < text.index("**Is the comparison fair?**")
            < text.index("**Do I have to change my agent or my model?**"))
    for needle in ("It gives your agent tools.", "so an agent that can start a local MCP server can be pointed at it",
                   "These are the core tools your agent gets:", "Structured file edits from a prepared plan",
                   "the tokens used times the model's published price", "It counts model tokens only.",
                   "In Claude Code, `/mcp` lists the connected servers.",
                   "Prefer to read the installer first? It is [install.sh](install.sh).",
                   "The names you will see in Simplicio's messages: Mapper observes,"):
        assert needle in text, needle
    for gone in ("did not pay for itself", "tokens served times", "applied as described", "the tools your agent sees most",
                 "a competent, widely used agent", "It is not handicapped"):
        assert gone not in text, gone
    # "Runtime" is only in the pinned vocabulary sentence; agents, not hosts.
    for line in text.splitlines():
        if "Runtime" in line:
            assert line.startswith("The names you will see in Simplicio's messages:"), line[:100]
    assert " host ids" not in text and "host guide" not in text.lower()
    assert "© 2026 SimpleTI. Simplicio is a registered proprietary software. All rights reserved." in text


# --------------------------------------------------------------------------
# (d) nothing that explains the mechanism
# --------------------------------------------------------------------------

# Case-insensitive regular expressions. Each one is a phrase that would say or
# hint HOW Simplicio reaches its result, or a claim the repository cannot back.
FORBIDDEN_PHRASES = (
    # the explanation of the gain
    r"generators?\b", r"code[- ]generation", r"codegen", r"writes? the file", r"\b0 llm tokens\b",
    r"zero llm tokens", r"zero[- ]token", r"\b0 tokens\b",
    r"pre-?fill", r"prompt[- ]?exec", r"session-start", r"appends? the map",
    # A hook may be named. What a hook does, and its events, are not said in public.
    r"prompt[- ]hooks?", r"session[- ]?start[- ]hooks?", r"pre-?tool[- ]?(?:use)?[- ]hooks?",
    r"hooks?\s+(?:that|which)\s+(?:write|writes|wrote|pre-?fill\w*|run|runs|ran|execute\w*|append\w*|inject\w*|fill\w*|edit\w*)",
    r"hooks?\s+(?:write|writes|wrote|pre-?fills?|run|runs|ran|execute|executes|append|appends|inject|injects|fill|fills)\b",
    r"hooks?\b[^.\n]{0,80}\bbefore the model", r"\bbefore the model'?s? (?:first )?(?:turn|request)",
    r"userpromptsubmit", r"sessionstart", r"pretooluse", r"subagentstart", r"hooks? pre-tool",
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
    # Only the upper-case marker: the compatibility matrix itself uses the lower-case word as a status.
    r"(?-i:\bUNVERIFIED\b)", r"\btodo\b", r"\btbd\b",
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
    # The plain statements about hooks: which programs they run, not what they do.
    "In agents whose hook interface the installer has verified, it also installs Simplicio's hooks there.",
    "The hooks it installs run local programs only (the Simplicio binary and, for optional plugins, local scripts); "
    "none of them contacts the network.",
)


def test_forbidden_list_does_not_catch_the_public_interface():
    for phrase in ALLOWED_PUBLIC_STRINGS:
        for pattern in FORBIDDEN_PHRASES:
            assert not re.search(pattern, phrase, re.IGNORECASE), (pattern, phrase)


@pytest.mark.parametrize("path", [README, REPORT, DATA, *FIGURE_FILES, CHART_SCRIPT], ids=lambda p: p.name)
def test_public_benchmark_texts_do_not_explain_the_mechanism(path):
    text = _read(path)
    hits = [pattern for pattern in FORBIDDEN_PHRASES if re.search(pattern, text, re.IGNORECASE)]
    assert not hits, f"{path.name} matches forbidden patterns: {hits}"


def test_hooks_are_named_plainly_in_two_places_only_and_never_described():
    readme, report = _read(README), _read(REPORT)
    plain = "In agents whose hook interface the installer has verified, it also installs Simplicio's hooks there."
    assert plain in readme
    assert "[INSTALL.md](INSTALL.md) says what the installer writes" in readme
    # The word appears in the README only in the installer paragraph and in the privacy item.
    for line in readme.splitlines():
        if "hook" in line.lower():
            allowed = line.startswith("**What the installer changes in your agent.**") or line.startswith("- **No analytics.**")
            assert allowed, line[:80]
    assert "hook" not in report.lower()
    # The setups are not enumerated in the measurement paragraph or in the report.
    assert "The baseline is Claude Code 2.1.330 with its own tools, no MCP server and no Simplicio configuration." in readme
    assert "No MCP server and no Simplicio configuration of any kind." in report
    assert "set up the way the installer sets it up for Claude Code (`INSTALL.md` lists what the installer writes)" in report
    assert "without its optional resident background process and with sign-in turned off" in report


@pytest.mark.parametrize("sentence", [
    "The prompt hook writes the files.",
    "A hook that writes the first files runs before the model.",
    "Hooks which pre-fill the project are installed.",
    "The session-start hook adds the map.",
    "The PreToolUse and UserPromptSubmit events are used.",
])
def test_a_description_of_what_a_hook_does_is_still_caught(sentence):
    hits = [pattern for pattern in FORBIDDEN_PHRASES if re.search(pattern, sentence, re.IGNORECASE)]
    assert hits, sentence


def test_readme_says_beta_the_way_install_md_does():
    text = _read(README)
    assert text.count("including during the beta") == 2
    assert "public beta" not in text.lower()


def test_flow_block_is_a_plain_link_for_maintainers_without_the_counts():
    text = _read(README)
    assert "<summary>For maintainers: the generated flow diagram</summary>" in text
    assert "[docs/flow/simplicio.svg](docs/flow/simplicio.svg)" in text
    assert not re.search(r"!\[[^\]]*\]\([^)]*simplicio\.svg\)", text)
    assert not re.search(r"<img[^>]*simplicio\.svg", text)
    for needle in ("scripts/generate_flow.py", "scripts/verify_flow_langflow.py", "docs/flow/README.md"):
        assert needle in text, needle
    assert not re.search(r"\b42 nodes\b|\b63 edges\b|\b27 steps\b", text)


def test_readme_icon_is_the_small_copy_of_the_same_artwork():
    text = _read(README)
    icon = ROOT / "assets" / "simplicio-icon-192.png"
    assert 'src="assets/simplicio-icon-192.png"' in text
    assert 'width="96" height="96"' in text
    assert "apps/desktop/public/icon.png" not in text
    data = icon.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert (width, height) == (192, 192)
    assert len(data) < 40_000, len(data)


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
