#!/usr/bin/env python3
"""Render the benchmark chart of the README from the public benchmark data.

Reads benchmarks/2026-11-22-standard-benchmark.json and writes two SVG files, one
for light pages and one for dark pages:

    assets/benchmark-2026-11-22-light.svg
    assets/benchmark-2026-11-22-dark.svg

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
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = Path("benchmarks/2026-11-22-standard-benchmark.json")
OUTPUTS = {
    "light": Path("assets/benchmark-2026-11-22-light.svg"),
    "dark": Path("assets/benchmark-2026-11-22-dark.svg"),
}

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
            "output": sum((Decimal(s["output_tokens"]) for s in steps), Decimal(0)),
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


PANELS = (
    ("wall", "Time for the whole job", fmt_time),
    ("cost", "Cost reported by the agent", fmt_cost),
    ("output", "Output tokens", fmt_tokens),
)


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
    for key, title, fmt in PANELS:
        values = ", ".join(
            f"{data['arms'][arm]['label']} {fmt(spread(totals, arm, key)[0])}" for arm in ARM_ORDER
        )
        parts.append(f"{title}: {values}.")
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
    add(f".g{{fill:{theme['grey']}}}")
    add(f".a{{fill:{theme['accent']}}}")
    add(f".w{{stroke:{theme['ink']};stroke-width:2;fill:none}}")
    add(f".z{{stroke:{theme['grid']};stroke-width:1}}")
    add("</style>")
    add(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="{theme["surface"]}" stroke="{theme["frame"]}"/>'
    )

    for index, (key, title, fmt) in enumerate(PANELS):
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
            add(
                f'<text class="{"vb" if accent else "v"}" x="{_n(label_x)}" y="{_n(text_y)}">'
                f"{escape(fmt(median))}</text>"
            )
    add("</svg>")
    return "\n".join(out) + "\n"


# -- files --------------------------------------------------------------------

def load(root: Path) -> dict:
    return json.loads((root / DATA_PATH).read_text(encoding="utf-8"))


def render_all(root: Path = ROOT) -> dict[Path, str]:
    data = load(root)
    return {OUTPUTS[name]: render(data, name) for name in OUTPUTS}


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
