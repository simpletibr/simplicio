#!/usr/bin/env python3
"""Render the benchmark figures of the README and the report from the public benchmark data.

Reads benchmarks/2026-11-22-standard-benchmark.json and writes five figures, each as
two SVG files, one for light pages and one for dark pages (see FIGURES):

    assets/benchmark-2026-11-22-{light,dark}.svg            the headline chart
    assets/benchmark-2026-11-22-sessions-{light,dark}.svg   every session, time against cost
    assets/benchmark-2026-11-22-work-{light,dark}.svg       model requests and tool calls
    assets/benchmark-2026-11-22-steps-{light,dark}.svg      time by step
    assets/benchmark-2026-11-22-memory-{light,dark}.svg     peak memory

The output is deterministic: the same data gives the same bytes, so the files
can be committed and checked. `--check` writes nothing and exits 1 when a
committed file is missing or differs from what this script would write.

Standard library only. No web fonts: the files are shown through an <img> tag,
which cannot load anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Callable
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = Path("benchmarks/2026-11-22-standard-benchmark.json")
ARM_ORDER = ("no-simplicio", "simplicio-3.14.0", "simplicio-3.15.0")
ACCENT_ARM = "simplicio-3.15.0"

# Colours by role. The accent is the validated series green of the data
# visualisation palette; the grey is the de-emphasis colour for the other bars.
THEMES = {
    "light": {
        "surface": "#ffffff", "frame": "#d1d9e0", "ink": "#1f2328", "ink2": "#59636e",
        "grid": "#d1d9e0", "grey": "#8c959f", "accent": "#008300",
    },
    "dark": {
        "surface": "#0d1117", "frame": "#30363d", "ink": "#f0f6fc", "ink2": "#9198a1",
        "grid": "#30363d", "grey": "#6e7681", "accent": "#0ca30c",
    },
}

FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'

# Geometry, in user units. The image is shown 840 wide on desktop and about 420
# wide on a phone, so every text is 19 units or more.
WIDTH = 840
HEIGHT = 408
MARGIN_TOP = 14
PANEL_HEIGHT = 120
PANEL_GAP = 10
TITLE_ROW = 36
ROW_PITCH = 28
BAR_HEIGHT = 20
BAR_RADIUS = 4
LABEL_X = 22
BAR_X0 = 234
BAR_SPAN = 468  # width of the longest whisker
VALUE_GAP = 10
NOTE_GAP = 12
FONT_BIG = 22
FONT_KEY = 19


# -- statistics ---------------------------------------------------------------

def _d(value) -> Decimal:
    return Decimal(str(value))


def _round(value: Decimal, places: int) -> str:
    return str(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def _median(values: list[Decimal]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def session_totals(data: dict) -> dict[str, list[dict[str, Decimal]]]:
    """Per setup, one record per session: the sum of its three steps."""
    totals: dict[str, list[dict[str, Decimal]]] = {arm: [] for arm in ARM_ORDER}
    for session in data["sessions"]:
        steps = session["steps"]
        totals[session["arm"]].append({
            "wall": sum((_d(s["wall_s"]) for s in steps), Decimal(0)),
            "cost": sum((_d(s["cost_usd_cli"]) for s in steps), Decimal(0)),
            # Token, request and tool-call counts are published per session, not per step.
            "output": Decimal(session["totals"]["output_tokens"]),
            "requests": Decimal(session["totals"]["model_requests"]),
            "tools": Decimal(session["totals"]["tool_calls"]),
            "rss": max(_d(s["peak_rss_mb"]) for s in steps),
        })
    return totals


def spread(totals: dict, arm: str, key: str) -> tuple[Decimal, Decimal, Decimal]:
    values = [record[key] for record in totals[arm]]
    return _median(values), min(values), max(values)


# -- value formats --------------------------------------------------------------

def fmt_time(value: Decimal) -> str:
    return f"{_round(value, 0)} s"


def fmt_cost(value: Decimal) -> str:
    return f"${_round(value, 4)}"


def fmt_tokens(value: Decimal) -> str:
    return f"{int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP)):,}"


def note_faster(baseline: Decimal, value: Decimal) -> str:
    return f"{_round(baseline / value, 1)}\u00d7 faster"


def note_less(baseline: Decimal, value: Decimal) -> str:
    return f"{_round((1 - value / baseline) * 100, 0)}% less"


def note_fewer(baseline: Decimal, value: Decimal) -> str:
    return f"{_round((1 - value / baseline) * 100, 0)}% fewer"


# key, panel label, value format, annotation of the accent row against the first setup
PANELS = (
    ("wall", "Time for the whole job", fmt_time, note_faster),
    ("cost", "Cost reported by the agent", fmt_cost, note_less),
    ("output", "Output tokens", fmt_tokens, note_fewer),
)
BASELINE_ARM = ARM_ORDER[0]


def annotation(totals: dict, key: str, note) -> str:
    return note(spread(totals, BASELINE_ARM, key)[0], spread(totals, ACCENT_ARM, key)[0])


# -- drawing ------------------------------------------------------------------

def _n(value: float | Decimal) -> str:
    """A short, stable number for SVG attributes."""
    text = _round(Decimal(str(value)), 2)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _bar_path(x: Decimal, y: Decimal, width: Decimal, height: Decimal, radius: Decimal) -> str:
    """A bar that is square at the baseline and has a rounded data end."""
    if width <= 2 * radius:
        return f"M{_n(x)} {_n(y)}h{_n(width)}v{_n(height)}h{_n(-width)}z"
    r = _n(radius)
    return (
        f"M{_n(x)} {_n(y)}H{_n(x + width - radius)}"
        f"A{r} {r} 0 0 1 {_n(x + width)} {_n(y + radius)}"
        f"V{_n(y + height - radius)}"
        f"A{r} {r} 0 0 1 {_n(x + width - radius)} {_n(y + height)}"
        f"H{_n(x)}z"
    )


def _description(data: dict, totals: dict) -> str:
    parts = [
        "Horizontal bars, median of 3 sessions per setup, with the lowest and highest session as a thin line.",
    ]
    for key, title, fmt, _note in PANELS:
        values = ", ".join(
            f"{data['arms'][arm]['label']} {fmt(spread(totals, arm, key)[0])}" for arm in ARM_ORDER
        )
        parts.append(f"{title}: {values}.")
    suffixes = ("", " cost", " output tokens")
    notes = ", ".join(
        annotation(totals, key, note) + suffix
        for (key, _title, _fmt, note), suffix in zip(PANELS, suffixes)
    )
    parts.append(f"{data['arms'][ACCENT_ARM]['label']} against {data['arms'][BASELINE_ARM]['label']}: {notes}.")
    return " ".join(parts)


def render(data: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    totals = session_totals(data)
    labels = {arm: data["arms"][arm]["label"] for arm in ARM_ORDER}
    out: list[str] = []
    add = out.append

    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">'
    )
    add(
        "<title id=\"title\">Same agent, same model, same task: time, cost and output tokens "
        "with no Simplicio, Simplicio 3.14.0 and Simplicio 3.15.0</title>"
    )
    add(f'<desc id="desc">{escape(_description(data, totals))}</desc>')
    add("<style>")
    add(f"text{{font-family:{FONT};fill:{theme['ink']}}}")
    add(f".t{{font-size:{FONT_BIG}px;font-weight:600;fill:{theme['ink2']}}}")
    add(f".n{{font-size:{FONT_BIG}px}}")
    add(f".nb{{font-size:{FONT_BIG}px;font-weight:700}}")
    add(f".v{{font-size:{FONT_BIG}px;font-weight:600}}")
    add(f".vb{{font-size:{FONT_BIG}px;font-weight:700}}")
    add(f".k{{font-size:{FONT_KEY}px;fill:{theme['ink2']}}}")
    add(f".m{{font-size:{FONT_KEY}px;font-weight:400;fill:{theme['ink2']}}}")
    add(f".g{{fill:{theme['grey']}}}")
    add(f".a{{fill:{theme['accent']}}}")
    add(f".w{{stroke:{theme['ink']};stroke-width:2;fill:none}}")
    add(f".z{{stroke:{theme['grid']};stroke-width:1}}")
    add("</style>")
    add(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="{theme["surface"]}" stroke="{theme["frame"]}"/>'
    )

    for index, (key, title, fmt, note) in enumerate(PANELS):
        top = MARGIN_TOP + index * (PANEL_HEIGHT + PANEL_GAP)
        highest = max(spread(totals, arm, key)[2] for arm in ARM_ORDER)
        scale = Decimal(BAR_SPAN) / highest

        add(f'<text class="t" x="{LABEL_X}" y="{top + 24}">{escape(title)}</text>')
        if index == 0:
            add(
                f'<text class="k" x="{WIDTH - LABEL_X}" y="{top + 23}" text-anchor="end">'
                "line: lowest to highest of 3 sessions</text>"
            )
        first_row = top + TITLE_ROW
        add(
            f'<line class="z" x1="{BAR_X0}" y1="{first_row + 1}" x2="{BAR_X0}" '
            f'y2="{first_row + 3 * ROW_PITCH - 1}"/>'
        )
        for row, arm in enumerate(ARM_ORDER):
            median, low, high = spread(totals, arm, key)
            row_top = first_row + row * ROW_PITCH
            bar_y = Decimal(row_top + (ROW_PITCH - BAR_HEIGHT) // 2)
            centre = bar_y + Decimal(BAR_HEIGHT) / 2
            text_y = centre + Decimal(8)
            accent = arm == ACCENT_ARM
            width = median * scale

            add(
                f'<text class="{"nb" if accent else "n"}" x="{LABEL_X}" y="{_n(text_y)}">'
                f"{escape(labels[arm])}</text>"
            )
            add(
                f'<path class="{"a" if accent else "g"}" '
                f'd="{_bar_path(Decimal(BAR_X0), bar_y, width, Decimal(BAR_HEIGHT), Decimal(BAR_RADIUS))}"/>'
            )
            x_low = Decimal(BAR_X0) + low * scale
            x_high = Decimal(BAR_X0) + high * scale
            cap = Decimal(5)
            add(
                f'<path class="w" d="M{_n(x_low)} {_n(centre)}H{_n(x_high)}'
                f"M{_n(x_low)} {_n(centre - cap)}V{_n(centre + cap)}"
                f'M{_n(x_high)} {_n(centre - cap)}V{_n(centre + cap)}"/>'
            )
            label_x = max(Decimal(BAR_X0) + width, x_high) + Decimal(VALUE_GAP)
            # The annotation is a second span of the value's own text, so it follows the value
            # whatever font the viewer has and cannot collide with it.
            extra = (
                f'<tspan class="m" dx="{NOTE_GAP}">{escape(annotation(totals, key, note))}</tspan>'
                if accent else ""
            )
            add(
                f'<text class="{"vb" if accent else "v"}" x="{_n(label_x)}" y="{_n(text_y)}">'
                f"{escape(fmt(median))}{extra}</text>"
            )
    add("</svg>")
    return "\n".join(out) + "\n"


# -- more figures ---------------------------------------------------------------
#
# The four figures below share the look of the hero chart: the same two themes,
# palette, font stack and opaque rounded card. Every text is 19 units or more.
# Setups are told apart by shape and fill as well as by colour, and every row or
# cluster carries the setup's name, so nothing has to be decoded from a legend.

def _median_of(totals: dict, arm: str, key: str) -> Decimal:
    return spread(totals, arm, key)[0]


def _step_values(data: dict, arm: str, step: int, field: str) -> list[Decimal]:
    return [
        _d(session["steps"][step - 1][field]) for session in data["sessions"] if session["arm"] == arm
    ]


def _arm_label(data: dict, arm: str) -> str:
    return data["arms"][arm]["label"]


def _style(theme: dict) -> list[str]:
    ink, ink2 = theme["ink"], theme["ink2"]
    return [
        "<style>",
        f"text{{font-family:{FONT};fill:{ink}}}",
        f".t{{font-size:{FONT_BIG}px;font-weight:600;fill:{ink2}}}",
        f".n{{font-size:{FONT_BIG}px}}",
        f".nb{{font-size:{FONT_BIG}px;font-weight:700}}",
        f".v{{font-size:{FONT_BIG}px;font-weight:600}}",
        f".vb{{font-size:{FONT_BIG}px;font-weight:700}}",
        f".k{{font-size:{FONT_KEY}px;fill:{ink2}}}",
        f".m{{font-size:{FONT_KEY}px;font-weight:400;fill:{ink2}}}",
        f".mb{{font-size:{FONT_KEY}px;font-weight:700}}",
        f".g{{fill:{theme['grey']}}}",
        f".a{{fill:{theme['accent']}}}",
        f".w{{stroke:{ink};stroke-width:2;fill:none}}",
        f".z{{stroke:{theme['grid']};stroke-width:1}}",
        f".ho{{fill:{theme['surface']};stroke:{theme['grey']};stroke-width:3}}",
        f".gs{{fill:{theme['grey']};stroke:{theme['surface']};stroke-width:2}}",
        f".as{{fill:{theme['accent']};stroke:{theme['surface']};stroke-width:2}}",
        "</style>",
    ]


def _open(theme_name: str, height: int, title: str, desc: str) -> list[str]:
    theme = THEMES[theme_name]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
    ]
    out += _style(theme)
    out.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" '
        f'fill="{theme["surface"]}" stroke="{theme["frame"]}"/>'
    )
    return out


def _marker(arm: str, cx: Decimal, cy: Decimal) -> str:
    """No Simplicio: hollow circle. Simplicio 3.14.0: filled square. Simplicio 3.15.0: filled diamond in the accent."""
    if arm == ARM_ORDER[0]:
        return f'<circle class="ho" cx="{_n(cx)}" cy="{_n(cy)}" r="8"/>'
    if arm == ARM_ORDER[1]:
        return f'<rect class="gs" x="{_n(cx - 8)}" y="{_n(cy - 8)}" width="16" height="16"/>'
    return (
        f'<path class="as" d="M{_n(cx)} {_n(cy - 11)}L{_n(cx + 11)} {_n(cy)}'
        f'L{_n(cx)} {_n(cy + 11)}L{_n(cx - 11)} {_n(cy)}z"/>'
    )


# -- sessions: one mark per session ---------------------------------------------------

SC_X0, SC_X1 = 96, 812      # plot area, left and right
SC_Y0, SC_Y1 = 82, 352      # plot area, top and bottom
SC_HEIGHT = 424


def _ceil_to(value: Decimal, step: Decimal) -> Decimal:
    return (value / step).to_integral_value(rounding="ROUND_CEILING") * step


def sessions_points(data: dict) -> dict[str, list[tuple[Decimal, Decimal]]]:
    """Per setup, the (time in seconds, cost in dollars) of each session, fastest first."""
    totals = session_totals(data)
    return {
        arm: sorted((record["wall"], record["cost"]) for record in totals[arm]) for arm in ARM_ORDER
    }


def render_sessions(data: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    points = sessions_points(data)
    labels = {arm: _arm_label(data, arm) for arm in ARM_ORDER}
    parts = []
    for arm in ARM_ORDER:
        marks = ", ".join(f"{fmt_time(wall)} and {fmt_cost(cost)}" for wall, cost in points[arm])
        parts.append(f"{labels[arm]}: {marks}.")
    desc = (
        "Scatter plot with one mark per session, nine in all. Across is the time for the whole job in "
        "seconds, up is the cost reported by the agent in dollars. Both scales start at zero. "
        "No Simplicio is hollow circles, Simplicio 3.14.0 is grey squares and Simplicio 3.15.0 is green diamonds. "
        + " ".join(parts)
    )
    out = _open(theme_name, SC_HEIGHT, "Every session, not only the median: time against cost", desc)
    add = out.append

    all_walls = [wall for arm in ARM_ORDER for wall, _ in points[arm]]
    all_costs = [cost for arm in ARM_ORDER for _, cost in points[arm]]
    x_max = _ceil_to(max(all_walls), Decimal(30))
    y_max = _ceil_to(max(all_costs), Decimal("0.005"))
    x_scale = Decimal(SC_X1 - SC_X0) / x_max
    y_scale = Decimal(SC_Y1 - SC_Y0) / y_max

    def px(wall: Decimal) -> Decimal:
        return Decimal(SC_X0) + wall * x_scale

    def py(cost: Decimal) -> Decimal:
        return Decimal(SC_Y1) - cost * y_scale

    add(f'<text class="t" x="{LABEL_X}" y="30">Every session, not only the median</text>')
    add(f'<text class="k" x="{LABEL_X}" y="58">Cost reported by the agent, in dollars</text>')

    # Light gridlines with tick labels. The axes start at zero.
    y_step = Decimal("0.01")
    tick = Decimal(0)
    while tick <= y_max:
        y = py(tick)
        add(f'<line class="z" x1="{SC_X0}" y1="{_n(y)}" x2="{SC_X1}" y2="{_n(y)}"/>')
        label = "$0" if tick == 0 else f"${_round(tick, 2)}"
        add(f'<text class="k" x="{SC_X0 - 10}" y="{_n(y + 7)}" text-anchor="end">{label}</text>')
        tick += y_step
    x_step = Decimal(50)
    tick = Decimal(0)
    while tick <= x_max:
        x = px(tick)
        add(f'<line class="z" x1="{_n(x)}" y1="{SC_Y0}" x2="{_n(x)}" y2="{SC_Y1}"/>')
        add(f'<text class="k" x="{_n(x)}" y="{SC_Y1 + 26}" text-anchor="middle">{int(tick)}</text>')
        tick += x_step
    add(
        f'<text class="k" x="{(SC_X0 + SC_X1) // 2}" y="{SC_Y1 + 54}" text-anchor="middle">'
        "Time for the whole job, in seconds</text>"
    )

    # Marks: the accent last, so it sits on top where marks overlap.
    for arm in ARM_ORDER:
        for wall, cost in points[arm]:
            add(_marker(arm, px(wall), py(cost)))

    # Names next to their clusters.
    cluster = {arm: [(px(w), py(c)) for w, c in points[arm]] for arm in ARM_ORDER}
    none_arm, prev_arm, new_arm = ARM_ORDER
    far = max(cluster[none_arm])  # the slowest session without Simplicio
    add(
        f'<text class="n" x="{_n(far[0] - 20)}" y="{_n(far[1] + 8)}" text-anchor="end">'
        f"{escape(labels[none_arm])}</text>"
    )
    # Below the squares: above them sits a hollow circle of another setup, and a label there would read as its own.
    bottom = max(y for _, y in cluster[prev_arm])
    centre = (min(x for x, _ in cluster[prev_arm]) + max(x for x, _ in cluster[prev_arm])) / 2
    add(
        f'<text class="n" x="{_n(centre)}" y="{_n(bottom + 42)}" text-anchor="middle">'
        f"{escape(labels[prev_arm])}</text>"
    )
    right = max(x for x, _ in cluster[new_arm])
    mid = (min(y for _, y in cluster[new_arm]) + max(y for _, y in cluster[new_arm])) / 2
    add(
        f'<text class="nb" x="{_n(right + 24)}" y="{_n(mid + 8)}">{escape(labels[new_arm])}</text>'
    )
    add("</svg>")
    return "\n".join(out) + "\n"


# -- work: one mark per request or per call ---------------------------------------------

WK_X0 = 224        # centre of the first mark is WK_X0 + WK_MARK_PITCH / 2
WK_PITCH = 22
WK_ROW = 34
WK_TITLE = 36
WK_HEIGHT = 366


def render_work(data: dict, theme_name: str) -> str:
    totals = session_totals(data)
    labels = {arm: _arm_label(data, arm) for arm in ARM_ORDER}
    blocks = (("requests", "Model requests"), ("tools", "Tool calls"))
    counts = {key: {arm: int(_median_of(totals, arm, key)) for arm in ARM_ORDER} for key, _ in blocks}
    parts = []
    for key, title in blocks:
        values = ", ".join(f"{labels[arm]} {counts[key][arm]}" for arm in ARM_ORDER)
        parts.append(f"{title}: {values}.")
    desc = (
        "Unit chart. Each mark is one model request or one tool call. Each row shows the median of "
        "3 sessions. No Simplicio is hollow circles, Simplicio 3.14.0 is grey squares and "
        "Simplicio 3.15.0 is green diamonds. " + " ".join(parts)
    )
    out = _open(theme_name, WK_HEIGHT, "What the model had to do: requests and tool calls", desc)
    add = out.append
    for block, (key, title) in enumerate(blocks):
        top = MARGIN_TOP + block * (WK_TITLE + 3 * WK_ROW + 16)
        add(f'<text class="t" x="{LABEL_X}" y="{top + 24}">{escape(title)}</text>')
        for row, arm in enumerate(ARM_ORDER):
            centre = Decimal(top + WK_TITLE + row * WK_ROW + WK_ROW // 2)
            accent = arm == ACCENT_ARM
            add(
                f'<text class="{"nb" if accent else "n"}" x="{LABEL_X}" y="{_n(centre + 8)}">'
                f"{escape(labels[arm])}</text>"
            )
            count = counts[key][arm]
            for index in range(count):
                add(_marker(arm, Decimal(WK_X0 + WK_PITCH // 2 + index * WK_PITCH), centre))
            end = Decimal(WK_X0 + WK_PITCH // 2 + (count - 1) * WK_PITCH) + Decimal(22)
            add(
                f'<text class="{"vb" if accent else "v"}" x="{_n(end)}" y="{_n(centre + 8)}">{count}</text>'
            )
    key_y = MARGIN_TOP + 2 * (WK_TITLE + 3 * WK_ROW + 16) + 14
    add(
        f'<text class="k" x="{LABEL_X}" y="{key_y}">Each mark is one model request or one tool call. '
        "Counts are the median of 3 sessions.</text>"
    )
    add("</svg>")
    return "\n".join(out) + "\n"


# -- steps: three panels on one scale ---------------------------------------------------

ST_PANEL_X0 = 214
ST_PANEL_PITCH = 202
ST_SCALE_MAX = 60       # seconds, the same for all three panels
ST_SCALE_SPAN = 118     # units that 60 seconds take
ST_TITLE = 36
ST_ROW = 36
ST_HEIGHT = 262
STEP_TITLES = ("1. Build", "2. Change", "3. Register")


def step_medians(data: dict) -> dict[str, list[Decimal]]:
    """Per setup, the median time of step 1, 2 and 3 in seconds."""
    return {
        arm: [_median(_step_values(data, arm, step, "wall_s")) for step in (1, 2, 3)] for arm in ARM_ORDER
    }


def render_steps(data: dict, theme_name: str) -> str:
    medians = step_medians(data)
    labels = {arm: _arm_label(data, arm) for arm in ARM_ORDER}
    parts = []
    for index, title in enumerate(STEP_TITLES):
        values = ", ".join(f"{labels[arm]} {_round(medians[arm][index], 1)} s" for arm in ARM_ORDER)
        parts.append(f"Step {title}: {values}.")
    desc = (
        "Three small panels side by side, one for each step of the job, on one shared scale from 0 to "
        f"{ST_SCALE_MAX} seconds. Each bar is the median time of 3 sessions. " + " ".join(parts)
    )
    out = _open(theme_name, ST_HEIGHT, "Time by step, median of 3 sessions, one scale for all three steps", desc)
    add = out.append
    scale = Decimal(ST_SCALE_SPAN) / Decimal(ST_SCALE_MAX)
    top = MARGIN_TOP
    first_row = top + ST_TITLE
    last_row_end = first_row + 3 * ST_ROW
    for row, arm in enumerate(ARM_ORDER):
        accent = arm == ACCENT_ARM
        centre = first_row + row * ST_ROW + ST_ROW // 2
        add(f'<text class="{"nb" if accent else "n"}" x="{LABEL_X}" y="{centre + 8}">{escape(labels[arm])}</text>')
    for index, title in enumerate(STEP_TITLES):
        x0 = ST_PANEL_X0 + index * ST_PANEL_PITCH
        add(f'<text class="t" x="{x0}" y="{top + 24}">{escape(title)}</text>')
        x60 = x0 + ST_SCALE_SPAN
        # The baseline of the bars, and a short scale rail under them. No line crosses a value label.
        add(f'<line class="z" x1="{x0}" y1="{first_row}" x2="{x0}" y2="{last_row_end}"/>')
        add(
            f'<path class="z" d="M{x0} {last_row_end + 8}V{last_row_end + 2}H{x60}V{last_row_end + 8}" fill="none"/>'
        )
        add(f'<text class="k" x="{x0}" y="{last_row_end + 26}" text-anchor="middle">0</text>')
        add(f'<text class="k" x="{x60}" y="{last_row_end + 26}" text-anchor="middle">{ST_SCALE_MAX} s</text>')
        for row, arm in enumerate(ARM_ORDER):
            accent = arm == ACCENT_ARM
            value = medians[arm][index]
            centre = Decimal(first_row + row * ST_ROW + ST_ROW // 2)
            bar_y = centre - Decimal(BAR_HEIGHT) / 2
            width = value * scale
            add(
                f'<path class="{"a" if accent else "g"}" '
                f'd="{_bar_path(Decimal(x0), bar_y, width, Decimal(BAR_HEIGHT), Decimal(BAR_RADIUS))}"/>'
            )
            add(
                f'<text class="{"vb" if accent else "v"}" x="{_n(Decimal(x0) + width + 8)}" y="{_n(centre + 8)}">'
                f"{_round(value, 1)} s</text>"
            )
    add(
        f'<text class="k" x="{LABEL_X}" y="{last_row_end + 62}">All three panels use the same scale, 0 to '
        f"{ST_SCALE_MAX} s. Bars are the median of 3 sessions.</text>"
    )
    add("</svg>")
    return "\n".join(out) + "\n"


# -- memory: the loss, in plain sight ---------------------------------------------------

MEM_HEIGHT = 150
MEM_SPAN = 380


def memory_notes(totals: dict) -> dict[str, str]:
    """Per setup other than the baseline, how much more memory it peaked at, in whole percent."""
    baseline = _median_of(totals, BASELINE_ARM, "rss")
    return {
        arm: f"{_round((_median_of(totals, arm, 'rss') / baseline - 1) * 100, 0)}% more"
        for arm in ARM_ORDER[1:]
    }


def render_memory(data: dict, theme_name: str) -> str:
    totals = session_totals(data)
    labels = {arm: _arm_label(data, arm) for arm in ARM_ORDER}
    notes = memory_notes(totals)
    parts = []
    for arm in ARM_ORDER:
        median, low, high = spread(totals, arm, "rss")
        text = f"{labels[arm]} {_round(median, 0)} MB, lowest to highest session {_round(low, 0)} to {_round(high, 0)} MB"
        text += ", the lowest of the three" if arm == BASELINE_ARM else f", {notes[arm]} than {labels[BASELINE_ARM]}"
        parts.append(text + ".")
    desc = "Peak memory, median of 3 sessions, with the lowest and highest session as a thin line. " + " ".join(parts)
    out = _open(theme_name, MEM_HEIGHT, "Peak memory: Simplicio uses more than the plain agent", desc)
    add = out.append
    top = MARGIN_TOP
    add(f'<text class="t" x="{LABEL_X}" y="{top + 24}">Peak memory</text>')
    add(
        f'<text class="k" x="{WIDTH - LABEL_X}" y="{top + 23}" text-anchor="end">'
        "line: lowest to highest of 3 sessions</text>"
    )
    highest = max(spread(totals, arm, "rss")[2] for arm in ARM_ORDER)
    scale = Decimal(MEM_SPAN) / highest
    first_row = top + TITLE_ROW
    add(
        f'<line class="z" x1="{BAR_X0}" y1="{first_row + 1}" x2="{BAR_X0}" '
        f'y2="{first_row + 3 * ROW_PITCH - 1}"/>'
    )
    for row, arm in enumerate(ARM_ORDER):
        median, low, high = spread(totals, arm, "rss")
        accent = arm == ACCENT_ARM
        row_top = first_row + row * ROW_PITCH
        bar_y = Decimal(row_top + (ROW_PITCH - BAR_HEIGHT) // 2)
        centre = bar_y + Decimal(BAR_HEIGHT) / 2
        text_y = centre + Decimal(8)
        width = median * scale
        add(f'<text class="{"nb" if accent else "n"}" x="{LABEL_X}" y="{_n(text_y)}">{escape(labels[arm])}</text>')
        add(
            f'<path class="{"a" if accent else "g"}" '
            f'd="{_bar_path(Decimal(BAR_X0), bar_y, width, Decimal(BAR_HEIGHT), Decimal(BAR_RADIUS))}"/>'
        )
        x_low = Decimal(BAR_X0) + low * scale
        x_high = Decimal(BAR_X0) + high * scale
        cap = Decimal(5)
        add(
            f'<path class="w" d="M{_n(x_low)} {_n(centre)}H{_n(x_high)}'
            f"M{_n(x_low)} {_n(centre - cap)}V{_n(centre + cap)}"
            f'M{_n(x_high)} {_n(centre - cap)}V{_n(centre + cap)}"/>'
        )
        label_x = max(Decimal(BAR_X0) + width, x_high) + Decimal(VALUE_GAP)
        tag = "lowest" if arm == BASELINE_ARM else notes[arm]
        add(
            f'<text class="{"vb" if accent else "v"}" x="{_n(label_x)}" y="{_n(text_y)}">'
            f'{_round(median, 0)} MB<tspan class="mb" dx="{NOTE_GAP}">{escape(tag)}</tspan></text>'
        )
    add("</svg>")
    return "\n".join(out) + "\n"

# -- the registry ---------------------------------------------------------------------

@dataclass(frozen=True)
class Figure:
    key: str
    stem: str
    render: Callable[[dict, str], str]


# One entry per figure this script writes. `--check` and the contract test walk this tuple.
FIGURES = (
    Figure("hero", "benchmark-2026-11-22", render),
    Figure("sessions", "benchmark-2026-11-22-sessions", render_sessions),
    Figure("work", "benchmark-2026-11-22-work", render_work),
    Figure("steps", "benchmark-2026-11-22-steps", render_steps),
    Figure("memory", "benchmark-2026-11-22-memory", render_memory),
)
THEME_NAMES = ("light", "dark")


def figure_path(figure: Figure, theme_name: str) -> Path:
    return Path("assets") / f"{figure.stem}-{theme_name}.svg"


# -- files --------------------------------------------------------------------

def load(root: Path) -> dict:
    return json.loads((root / DATA_PATH).read_text(encoding="utf-8"))


def render_all(root: Path = ROOT) -> dict[Path, str]:
    data = load(root)
    return {
        figure_path(figure, theme_name): figure.render(data, theme_name)
        for figure in FIGURES
        for theme_name in THEME_NAMES
    }


def write(root: Path = ROOT) -> list[str]:
    written = []
    for relative, text in render_all(root).items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
        written.append(relative.as_posix())
    return written


def check(root: Path = ROOT) -> list[str]:
    """The committed files that are missing or differ from what `write` would produce."""
    stale = []
    for relative, text in render_all(root).items():
        target = root / relative
        if not target.is_file() or target.read_bytes() != text.encode("utf-8"):
            stale.append(relative.as_posix())
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 if a committed SVG is stale")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    if args.check:
        stale = check(args.root)
        if stale:
            for relative in stale:
                print(f"stale or missing: {relative}", file=sys.stderr)
            print("run: python3 scripts/render_benchmark_chart.py", file=sys.stderr)
            return 1
        print("benchmark chart: up to date")
        return 0
    for relative in write(args.root):
        print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
