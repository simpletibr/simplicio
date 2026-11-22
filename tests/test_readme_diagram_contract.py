"""The README diagram "where Simplicio runs" must match its script and its words.

The two SVG files under assets/ are written by scripts/render_readme_diagram.py.
They must be what the script writes, they must load nothing from outside, they
must carry exactly the labels the product facts allow (no more, no fewer), and
they must not explain how the product works inside.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "render_readme_diagram.py"
SVGS = (
    ROOT / "assets" / "diagram-where-simplicio-runs-light.svg",
    ROOT / "assets" / "diagram-where-simplicio-runs-dark.svg",
)
SVG_NS = "{http://www.w3.org/2000/svg}"

# Every label of the picture, as a reader sees it. A label that the picture
# breaks over two lines is listed here as one line.
LABELS = (
    "Your machine",
    "As of Simplicio 3.15.0",
    "You",
    "Your coding agent",
    "Claude Code, Codex, Cursor, ...",
    "Simplicio",
    "one signed binary, started by your agent",
    "Your repository",
    "local STDIO (MCP)",
    "maps, reads, edits, checks",
    "Your model provider",
    "prompts and code, as before",
    "SimpleTI",
    "sign-in and plan check",
    "no repository content",
    "GitHub",
    "release check",
    "no data about you or your code",
)

# Words the picture must not use: they would explain how the product works inside.
FORBIDDEN_WORDS = (
    "hook", "generator", "codegen", "route", "routing", "fill", "gate", "refusal",
    "threshold", "tokio", "facade", "offline",
)

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _module():
    spec = importlib.util.spec_from_file_location("render_readme_diagram", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _readable(path: Path) -> dict[str, list[str]]:
    """What a reader or a screen reader gets: the labels, the title and the description.

    The two lines of a label that breaks over two lines are joined by one space.
    """
    root = ET.fromstring(_read(path))
    texts = [
        " ".join(" ".join(part.split()) for part in element.itertext() if part.strip())
        for element in root.iter(SVG_NS + "text")
    ]
    title = "".join(root.find(SVG_NS + "title").itertext())
    desc = "".join(root.find(SVG_NS + "desc").itertext())
    return {"texts": texts, "title": [title], "desc": [desc]}


def _words(pattern_words: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile(r"\b(?:" + "|".join(pattern_words) + r")", re.IGNORECASE)


# --------------------------------------------------------------------------
# The files are what the script writes
# --------------------------------------------------------------------------

def test_committed_svgs_are_what_the_script_would_write():
    module = _module()
    assert module.check() == []
    written = module.render_all()
    assert {path.name for path in written} == {path.name for path in SVGS}
    for path in SVGS:
        assert path.read_bytes() == written[Path("assets") / path.name].encode("utf-8"), path.name


def test_script_check_flag_exits_zero_when_current():
    done = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stdout + done.stderr


def test_script_check_flag_exits_non_zero_for_a_stale_or_missing_file(tmp_path):
    module = _module()
    module.write(tmp_path)
    assert module.main(["--check", "--root", str(tmp_path)]) == 0
    stale = tmp_path / "assets" / SVGS[0].name
    stale.write_text(stale.read_text(encoding="utf-8").replace("Your machine", "My machine", 1), encoding="utf-8")
    assert module.main(["--check", "--root", str(tmp_path)]) == 1
    stale.unlink()
    assert module.main(["--check", "--root", str(tmp_path)]) == 1


def test_script_is_deterministic(tmp_path):
    module = _module()
    first = module.render_all()
    assert first == module.render_all()
    module.write(tmp_path)
    for relative, text in first.items():
        assert (tmp_path / relative).read_bytes() == text.encode("utf-8")


# --------------------------------------------------------------------------
# Self-contained and accessible
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_svg_is_self_contained_and_accessible(path):
    text = _read(path)
    assert text.startswith("<svg"), path.name
    assert 'width="840"' in text and 'viewBox="0 0 840 ' in text, path.name
    assert "<title" in text and "<desc" in text, path.name
    assert 'role="img"' in text and 'aria-labelledby="title desc"' in text, path.name
    for forbidden in ("@import", "url(http", "<image", "<script", "xlink:href", "<foreignObject", "href="):
        assert forbidden not in text, (path.name, forbidden)
    ET.fromstring(text)  # well-formed XML
    fonts = re.findall(r"font-family:([^;}]*)", text)
    assert fonts and all("sans-serif" in font and "http" not in font for font in fonts), path.name


@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_no_text_is_smaller_than_19_units(path):
    sizes = [int(size) for size in re.findall(r"font-size:(\d+)px", _read(path))]
    assert sizes and min(sizes) >= 19, (path.name, sizes)


@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_description_says_what_the_picture_shows(path):
    desc = _readable(path)["desc"][0]
    for label in LABELS:
        assert label in desc, (path.name, label)
    assert "dashed" in desc


# --------------------------------------------------------------------------
# The words
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_svg_carries_every_label_and_nothing_else(path):
    texts = _readable(path)["texts"]
    assert sorted(texts) == sorted(LABELS), (path.name, sorted(set(texts) ^ set(LABELS)))


@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_svg_does_not_explain_the_inside_of_the_product(path):
    # Every word is checked against everything a reader gets: the labels, the title and the description.
    readable = " ".join(part for parts in _readable(path).values() for part in parts)
    hits = sorted({m.group(0).lower() for m in _words(FORBIDDEN_WORDS).finditer(readable)})
    assert not hits, (path.name, hits)
    # The markup of an SVG must use the `fill` attribute to colour a shape, so the whole file is checked
    # against every forbidden word except that one.
    markup_words = tuple(word for word in FORBIDDEN_WORDS if word != "fill")
    hits = sorted({m.group(0).lower() for m in _words(markup_words).finditer(_read(path))})
    assert not hits, (path.name, hits)


# --------------------------------------------------------------------------
# The two themes are one picture
# --------------------------------------------------------------------------

def test_the_two_themes_differ_only_in_colour():
    light, dark = (HEX.sub("#", _read(path)) for path in SVGS)
    assert light == dark
    assert set(HEX.findall(_read(SVGS[0]))) != set(HEX.findall(_read(SVGS[1])))


@pytest.mark.parametrize("path, accent", list(zip(SVGS, ("#008300", "#0ca30c"))), ids=lambda v: getattr(v, "name", v))
def test_simplicio_is_the_only_accent_element(path, accent):
    text = _read(path)
    assert text.lower().count(accent) == 1, (path.name, accent)
    root = ET.fromstring(text)
    accent_class = re.search(r"\.(\w+)\{fill:" + re.escape(accent) + r"\}", text).group(1)
    users = [element for element in root.iter() if accent_class in (element.get("class") or "").split()]
    assert [element.tag for element in users] == [SVG_NS + "rect"], path.name
    # The accent box is the one that sits above the word "Simplicio".
    box_x, box_w = float(users[0].get("x")), float(users[0].get("width"))
    titles = [
        element for element in root.iter(SVG_NS + "text")
        if "".join(element.itertext()) == "Simplicio" and element.get("x")
    ]
    assert len(titles) == 1 and abs(float(titles[0].get("x")) - (box_x + box_w / 2)) < 0.01, path.name


# --------------------------------------------------------------------------
# What stays and what leaves
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", SVGS, ids=lambda p: p.name)
def test_three_links_stay_solid_inside_and_three_dashed_links_end_outside(path):
    root = ET.fromstring(_read(path))
    text = _read(path)
    css = dict(re.findall(r"\.(\w+)\{([^}]*)\}", text))
    solid = [e for e in root.iter(SVG_NS + "line") if "dasharray" not in css[e.get("class")]]
    dashed = [e for e in root.iter(SVG_NS + "line") if "dasharray" in css[e.get("class")]]
    assert len(solid) == 3 and len(dashed) == 3, (len(solid), len(dashed))
    # The big box is the first rect of the class that is neither the card nor a box of the picture.
    rects = [e for e in root.iter(SVG_NS + "rect") if e.get("class")]
    big = max(rects, key=lambda e: float(e.get("width")) * float(e.get("height")))
    left, top = float(big.get("x")), float(big.get("y"))
    right, bottom = left + float(big.get("width")), top + float(big.get("height"))
    for line in solid:
        for key in ("x1", "x2"):
            assert left < float(line.get(key)) < right, (path.name, "a solid link leaves the box")
        for key in ("y1", "y2"):
            assert top < float(line.get(key)) < bottom, (path.name, "a solid link leaves the box")
    for line in dashed:
        assert float(line.get("y1")) < bottom < float(line.get("y2")), (path.name, "a dashed link must cross the edge")
        assert float(line.get("y2")) > bottom + 30, (path.name, "a dashed link must end well outside the box")
    # An arrow head at the end of every link.
    assert len(list(root.iter(SVG_NS + "polygon"))) == 6
