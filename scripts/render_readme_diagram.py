#!/usr/bin/env python3
"""Render the README diagram "where Simplicio runs and what leaves your machine".

Writes two SVG files, one for light pages and one for dark pages, with the same
layout. The big box is "Your machine". Links that stay inside it are solid; the
three links that end outside it are dashed. Where a link ends says which kind it
is, so the picture needs no legend. Simplicio is the only accent-coloured box.

    assets/diagram-where-simplicio-runs-light.svg
    assets/diagram-where-simplicio-runs-dark.svg

The output is deterministic: the same script gives the same bytes, so the files
can be committed and checked. `--check` writes nothing and exits 1 when a
committed file is missing or differs from what this script would write.

Standard library only. No web fonts and no external resource: the files are
shown through an <img> tag, which cannot load anything.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {
    "light": Path("assets/diagram-where-simplicio-runs-light.svg"),
    "dark": Path("assets/diagram-where-simplicio-runs-dark.svg"),
}

# Colours by role, the same values as the benchmark chart. `subtle` tints the
# machine box; `on_accent` is the text colour that reads on the accent.
THEMES = {
    "light": {
        "surface": "#ffffff", "frame": "#d1d9e0", "ink": "#1f2328", "ink2": "#59636e",
        "grey": "#8c959f", "accent": "#008300", "subtle": "#f6f8fa", "on_accent": "#ffffff",
    },
    "dark": {
        "surface": "#0d1117", "frame": "#30363d", "ink": "#f0f6fc", "ink2": "#9198a1",
        "grey": "#6e7681", "accent": "#0ca30c", "subtle": "#161b22", "on_accent": "#0d1117",
    },
}

FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'

# -- the words ----------------------------------------------------------------
# Every label of the picture. A list is a label on several lines.

MACHINE = "Your machine"
NOTE = "As of Simplicio 3.15.0"
YOU = "You"
AGENT = "Your coding agent"
AGENT_SUB = "Claude Code, Codex, Cursor, ..."
SIMPLICIO = "Simplicio"
SIMPLICIO_SUB = ["one signed binary,", "started by your agent"]
REPOSITORY = "Your repository"
PROVIDER = "Your model provider"
SIMPLETI = "SimpleTI"
SIMPLETI_SUB = "no repository content"
GITHUB = "GitHub"
GITHUB_SUB = ["no data about you", "or your code"]
LINK_STDIO = ["local STDIO", "(MCP)"]
LINK_REPOSITORY = "maps, reads, edits, checks"
LINK_PROVIDER = ["prompts and", "code, as before"]
LINK_SIMPLETI = ["sign-in and", "plan check"]
LINK_GITHUB = "release check"

TITLE = "Where Simplicio runs and what leaves your machine"
DESCRIPTION = (
    "A large box labelled Your machine holds You, Your coding agent (Claude Code, Codex, Cursor, ...), "
    "Simplicio (one signed binary, started by your agent) and Your repository. You work with your coding agent. "
    "The agent talks to Simplicio over local STDIO (MCP), and Simplicio maps, reads, edits, checks your repository. "
    "Three dashed links leave the box. From your coding agent to Your model provider: prompts and code, as before. "
    "From Simplicio to SimpleTI: sign-in and plan check, no repository content. "
    "From Simplicio to GitHub: release check, no data about you or your code. "
    "As of Simplicio 3.15.0."
)

# -- geometry, in user units --------------------------------------------------
# The image is shown 840 wide on a desktop and about 420 wide on a phone, so
# every text is 19 units or more.

WIDTH = 840
HEIGHT = 486
FONT_BOX = 23       # the name of a box
FONT_HERO = 26      # the name of the Simplicio box
FONT_SMALL = 19     # second lines, link labels, the note
FONT_MACHINE = 22   # the label of the big box
LINE = 23           # distance between two lines of one label
CAP_SHIFT = 6.5     # baseline below the optical middle of a 19 unit line

MACHINE_BOX = (16, 16, 808, 288)             # x, y, width, height
MACHINE_BOTTOM = MACHINE_BOX[1] + MACHINE_BOX[3]

TOP_ROW = (62, 50)                           # y, height: You and the repository
BOTTOM_ROW = (172, 112)                      # y, height: the agent and Simplicio
OUTSIDE_ROW = (380, 90)                      # y, height: the three destinations

AGENT_BOX = (40, 308)                        # x, width
SIMPLICIO_BOX = (484, 316)
YOU_BOX = (134, 120)
REPOSITORY_BOX = (525, 230)
PROVIDER_BOX = (40, 308)
SIMPLETI_BOX = (396, 222)
GITHUB_BOX = (634, 190)

LABEL_GAP = 14       # between an arrow and the label beside it
ARROW_WIDTH = 2.5
HEAD_LENGTH = 13
HEAD_HALF = 7
DASH = "9 7"


def _n(value: float) -> str:
    """A short, stable number for SVG attributes."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _centre(box: tuple[float, float]) -> float:
    return box[0] + box[1] / 2


def _right(box: tuple[float, float]) -> float:
    return box[0] + box[1]


# -- a guard against clipped words --------------------------------------------
# SVG cannot measure text. These are generous widths, above what Helvetica,
# Arial, Segoe UI and Inter give; the render is still looked at. A box whose
# text would come within 8 units of its edge makes the script stop.

def _estimate(text: str, size: float, bold: bool = False) -> float:
    return len(text) * size * (0.58 if bold else 0.49)


def _fits(text: str, size: float, width: float, bold: bool = False, pad: float = 8) -> None:
    need = _estimate(text, size, bold) + 2 * pad
    if need > width:
        raise SystemExit(f"text does not fit: {text!r} needs about {need:.0f}, the box is {width:.0f} wide")


# -- drawing ------------------------------------------------------------------

def _rect(x: float, y: float, w: float, h: float, rx: float, cls: str) -> str:
    return f'<rect class="{cls}" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="{_n(rx)}"/>'


def _lines(x: float, first_baseline: float, lines: list[str], cls: str, anchor: str = "middle") -> str:
    """One <text> with one <tspan> per line, the first line on `first_baseline`."""
    body = "".join(
        f'<tspan x="{_n(x)}" y="{_n(first_baseline + index * LINE)}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text class="{cls}" text-anchor="{anchor}">{body}</text>'


def _middle(middle: float, count: int) -> float:
    """The first baseline of `count` lines whose block is centred on `middle`."""
    return middle - (count - 1) * LINE / 2 + CAP_SHIFT


def _text(x: float, y: float, text: str, cls: str, anchor: str = "middle") -> str:
    return f'<text class="{cls}" x="{_n(x)}" y="{_n(y)}" text-anchor="{anchor}">{escape(text)}</text>'


def _arrow(x1: float, y1: float, x2: float, y2: float, cls: str) -> str:
    """A straight horizontal or vertical arrow whose head is a polygon at (x2, y2)."""
    dx = (x2 > x1) - (x2 < x1)
    dy = (y2 > y1) - (y2 < y1)
    assert (dx == 0) != (dy == 0), "arrows are horizontal or vertical"
    base_x, base_y = x2 - dx * HEAD_LENGTH, y2 - dy * HEAD_LENGTH
    px, py = dy * HEAD_HALF, dx * HEAD_HALF
    points = f"{_n(x2)},{_n(y2)} {_n(base_x + px)},{_n(base_y + py)} {_n(base_x - px)},{_n(base_y - py)}"
    # The line stops inside the head so a dashed line never leaves a gap before it.
    end_x, end_y = x2 - dx * (HEAD_LENGTH - 1), y2 - dy * (HEAD_LENGTH - 1)
    return (
        f'<line class="{cls}" x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(end_x)}" y2="{_n(end_y)}"/>'
        f'<polygon class="{cls}h" points="{points}"/>'
    )


def _box_text(box: tuple[float, float], row: tuple[float, float], title: str, sub: list[str] | str | None,
              title_cls: str = "bt", sub_cls: str = "bs", title_size: float = FONT_BOX) -> list[str]:
    """The name of a box and, under it, up to two small lines, centred in the box."""
    sub_lines = [sub] if isinstance(sub, str) else list(sub or [])
    x, y, h = _centre(box), row[0], row[1]
    _fits(title, title_size, box[1], bold=True)
    for line in sub_lines:
        _fits(line, FONT_SMALL, box[1])
    gap = 9  # between the name and the first small line
    block = title_size + (gap + FONT_SMALL + (len(sub_lines) - 1) * LINE if sub_lines else 0)
    top = y + (h - block) / 2
    out = [_text(x, top + title_size * 0.78, title, title_cls)]
    if sub_lines:
        out.append(_lines(x, top + title_size + gap + FONT_SMALL * 0.78, sub_lines, sub_cls))
    return out


def render(theme_name: str) -> str:
    theme = THEMES[theme_name]
    out: list[str] = []
    add = out.append

    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">'
    )
    add(f'<title id="title">{escape(TITLE)}</title>')
    add(f'<desc id="desc">{escape(DESCRIPTION)}</desc>')
    add("<style>")
    add(f"text{{font-family:{FONT};fill:{theme['ink']}}}")
    add(f".mt{{font-size:{FONT_MACHINE}px;font-weight:600;fill:{theme['ink2']}}}")
    add(f".nt{{font-size:{FONT_SMALL}px;fill:{theme['ink2']}}}")
    add(f".bt{{font-size:{FONT_BOX}px;font-weight:700}}")
    add(f".bs{{font-size:{FONT_SMALL}px;fill:{theme['ink2']}}}")
    add(f".st{{font-size:{FONT_HERO}px;font-weight:700;fill:{theme['on_accent']}}}")
    add(f".ss{{font-size:{FONT_SMALL}px;fill:{theme['on_accent']}}}")
    add(f".lb{{font-size:{FONT_SMALL}px;fill:{theme['ink2']}}}")
    add(f".m{{fill:{theme['subtle']};stroke:{theme['grey']};stroke-width:1.5}}")
    add(f".b{{fill:{theme['surface']};stroke:{theme['ink2']};stroke-width:1.5}}")
    add(f".o{{fill:{theme['surface']};stroke:{theme['grey']};stroke-width:1.5}}")
    add(f".s{{fill:{theme['accent']}}}")
    add(f".l{{stroke:{theme['ink2']};stroke-width:{ARROW_WIDTH};fill:none}}")
    add(f".lh{{fill:{theme['ink2']}}}")
    add(f".x{{stroke:{theme['ink']};stroke-width:{ARROW_WIDTH};stroke-dasharray:{DASH};fill:none}}")
    add(f".xh{{fill:{theme['ink']}}}")
    add("</style>")
    add(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="{theme["surface"]}" stroke="{theme["frame"]}"/>'
    )

    # The big box and its label, and the note in its corner.
    mx, my, mw, mh = MACHINE_BOX
    add(_rect(mx, my, mw, mh, 16, "m"))
    add(_text(mx + 24, my + 34, MACHINE, "mt", "start"))
    add(_text(mx + mw - 24, my + 34, NOTE, "nt", "end"))

    top_y, top_h = TOP_ROW
    bottom_y, bottom_h = BOTTOM_ROW
    out_y, out_h = OUTSIDE_ROW
    bottom_mid = bottom_y + bottom_h / 2
    agent_x = _centre(AGENT_BOX)
    repository_x = _centre(REPOSITORY_BOX)

    # The four boxes inside.
    add(_rect(YOU_BOX[0], top_y, YOU_BOX[1], top_h, top_h / 2, "b"))
    out.extend(_box_text(YOU_BOX, TOP_ROW, YOU, None))
    add(_rect(REPOSITORY_BOX[0], top_y, REPOSITORY_BOX[1], top_h, 12, "b"))
    out.extend(_box_text(REPOSITORY_BOX, TOP_ROW, REPOSITORY, None))
    add(_rect(AGENT_BOX[0], bottom_y, AGENT_BOX[1], bottom_h, 12, "b"))
    out.extend(_box_text(AGENT_BOX, BOTTOM_ROW, AGENT, AGENT_SUB))
    add(_rect(SIMPLICIO_BOX[0], bottom_y, SIMPLICIO_BOX[1], bottom_h, 12, "s"))
    out.extend(_box_text(SIMPLICIO_BOX, BOTTOM_ROW, SIMPLICIO, SIMPLICIO_SUB, "st", "ss", FONT_HERO))

    # Links that stay on the machine: solid.
    add(_arrow(agent_x, top_y + top_h, agent_x, bottom_y, "l"))
    add(_arrow(_right(AGENT_BOX), bottom_mid, SIMPLICIO_BOX[0], bottom_mid, "l"))
    add(_arrow(repository_x, bottom_y, repository_x, top_y + top_h, "l"))
    link_gap_x = (_right(AGENT_BOX) + SIMPLICIO_BOX[0]) / 2
    add(_lines(link_gap_x, _middle(bottom_mid - 36, len(LINK_STDIO)), LINK_STDIO, "lb"))
    add(_lines(repository_x - LABEL_GAP, _middle((top_y + top_h + bottom_y) / 2, 1), [LINK_REPOSITORY], "lb", "end"))

    # The three destinations, outside the big box: dashed, because they end there.
    # Each label stands beside its arrow, on the side that has room, and the first
    # lines of the three labels share a baseline.
    destinations = (
        (PROVIDER_BOX, PROVIDER, None, agent_x, LINK_PROVIDER, "start"),
        (SIMPLETI_BOX, SIMPLETI, SIMPLETI_SUB, _centre(SIMPLETI_BOX), LINK_SIMPLETI, "end"),
        (GITHUB_BOX, GITHUB, GITHUB_SUB, _centre(GITHUB_BOX), [LINK_GITHUB], "end"),
    )
    label_baseline = MACHINE_BOTTOM + 36
    for box, title, sub, x, label, anchor in destinations:
        add(_rect(box[0], out_y, box[1], out_h, 12, "o"))
        out.extend(_box_text(box, OUTSIDE_ROW, title, sub))
        add(_arrow(x, bottom_y + bottom_h, x, out_y, "x"))
        add(_lines(x + (LABEL_GAP if anchor == "start" else -LABEL_GAP), label_baseline, label, "lb", anchor))

    add("</svg>")
    return "\n".join(out) + "\n"


# -- files --------------------------------------------------------------------

def render_all() -> dict[Path, str]:
    return {OUTPUTS[name]: render(name) for name in OUTPUTS}


def write(root: Path = ROOT) -> list[str]:
    written = []
    for relative, text in render_all().items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
        written.append(relative.as_posix())
    return written


def check(root: Path = ROOT) -> list[str]:
    """The committed files that are missing or differ from what `write` would produce."""
    stale = []
    for relative, text in render_all().items():
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
            print("run: python3 scripts/render_readme_diagram.py", file=sys.stderr)
            return 1
        print("readme diagram: up to date")
        return 0
    for relative in write(args.root):
        print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
