"""Translation contract for READMEs/README.<lang>.md.

Each of the 14 localized files must be a faithful, full translation of README.md.
Prose is translated. Everything that carries a fact is kept: code, commands, file
names, links, numbers, units, agent and product names, the structure of the page.

Every test is parametrized by language, so a translator runs only its own file:

    python3 -m pytest tests/test_readme_translations_contract.py -q -p no:cacheprovider -k es-ES

The tests are numbered R01 to R14. A failure says which rule broke and, line by line,
what differs and how to fix it, so it can be repaired without reading this file.
"""

from __future__ import annotations

import functools
import html
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
ENGLISH = ROOT / "README.md"
LANGS = (
    "ar-SA", "es-ES", "fr-FR", "he-IL", "hi-IN", "id-ID", "it-IT",
    "ja-JP", "ko-KR", "ms-MY", "pl-PL", "pt-BR", "ru-RU", "zh-CN",
)
SHOWN = 8  # problems listed per failure
CODE_MARK = "\u0000CODE\u0000"

FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^`\n]*)$")
TAG_RE = re.compile(r"<[^>]+>")
PARA_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.DOTALL)
LANG_LINK_RE = re.compile(r'href="[^"]*README(?:\.[A-Za-z]{2}-[A-Za-z]{2})?\.md"')
PICTURE_RE = re.compile(
    r'<picture>\s*<source media="\(prefers-color-scheme: dark\)" srcset="([^"]+)">\s*'
    r'<img src="([^"]+)" width="840" alt="([^"]*)">\s*</picture>'
)
# A number with its separators and, when it has one, its unit: 121 s, $0.0226, 18,162, 375 MB, 39%, 4.9x.
NUMBER_RE = re.compile(r"\$?\d+(?:[.,]\d+)*(?:[\u00a0 ]?(?:MB|s|%|\u00d7)(?![A-Za-z]))?")

# What a non-Latin file must show in most of its prose lines.
SCRIPT = {
    "ar-SA": "\u0600-\u06ff", "he-IL": "\u0590-\u05ff", "hi-IN": "\u0900-\u097f",
    "ja-JP": "\u3040-\u30ff\u4e00-\u9fff", "ko-KR": "\uac00-\ud7af", "ru-RU": "\u0400-\u04ff",
    "zh-CN": "\u4e00-\u9fff",
}
# Words that are English and nothing else. A translated page has almost none of them.
ENGLISH_WORDS = {
    "the", "and", "with", "your", "you", "this", "that", "from", "are", "not", "what", "does", "which",
    "when", "where", "does", "has", "have", "will", "can",
}
# Rules 8 and 9: how much of the prose may stay identical to the English lines.
IDENTICAL_LINE_SHARE = 0.05      # at most 5% of the prose lines of 30 characters or more (4 of about 90)
SUBSTANTIAL_LINE = 30
SCRIPT_LINE_SHARE = 0.80         # non-Latin files: at least 80% of those lines carry the script
ENGLISH_WORD_SHARE = 0.02        # at most 2% of all words may be English words

# Strings and links that belonged to the old pages and must not survive in any language.
REMOVED_STRINGS = ("3.9.2", "46MB", "46 MB", "npm install", "npx", "100% Rust", "cold start", "simplicio-hero",
                   "benchmark-2026-10-31", "benchmark-2026-11-01", "2026-10-31", "2026-11-01", "multi-model", "map-codegen")
REMOVED_PATTERNS = (r"(?<![A-Za-z])brew ", r"(?<![A-Za-z])bun ")

# The brand line: the same English text in every language, never translated.
TAGLINE = "<p><b>UltraFast Mode for all.</b></p>"

# Strings other tests pin in every localized file.
PINNED = (
    "simplicio-installer", "pip install", "install.sh", "install.ps1",
    "python3 -m pip install --upgrade simplicio-installer", "simplicio install",
    "curl -fsSL https://raw.githubusercontent.com/simpletibr/simplicio/master/install.sh | sh",
    "irm https://raw.githubusercontent.com/simpletibr/simplicio/master/install.ps1 | iex",
)


# --------------------------------------------------------------------------
# Reading a page
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Doc:
    raw: str
    outside: str                      # the page with every fenced block replaced by one marker line
    blocks: tuple                     # (info string, content) of every fenced block, in order
    bar: str | None                   # the language bar paragraph
    notice: str | None                # the translation notice paragraph (translations only)
    body: str                         # outside, without the bar and the notice


def _split_fences(text: str):
    out, blocks, current, opened = [], [], [], None
    for line in text.split("\n"):
        if opened is None:
            match = FENCE_RE.match(line)
            if match:
                opened = (match.group("fence")[0], len(match.group("fence")), match.group("info").strip())
                current = []
                out.append(CODE_MARK)
            else:
                out.append(line)
        else:
            stripped = line.strip()
            if stripped and set(stripped) == {opened[0]} and len(stripped) >= opened[1]:
                blocks.append((opened[2], "\n".join(current) + "\n"))
                opened = None
            else:
                current.append(line)
    if opened is not None:
        blocks.append((opened[2], "\n".join(current) + "\n"))
    return "\n".join(out), tuple(blocks)


def parse(text: str) -> Doc:
    text = text.replace("\r\n", "\n")
    outside, blocks = _split_fences(text)
    bar = bar_span = notice = notice_span = None
    for match in PARA_RE.finditer(outside):
        if len(LANG_LINK_RE.findall(match.group(0))) >= 10:
            bar, bar_span = match.group(0), match.span()
            break
    if bar_span:
        for match in PARA_RE.finditer(outside, bar_span[1]):
            if 'href="../README.md"' in match.group(0):
                notice, notice_span = match.group(0), match.span()
                break
    body = outside
    for span in sorted(filter(None, (bar_span, notice_span)), reverse=True):
        body = body[: span[0]] + body[span[1]:]
    return Doc(text, outside, blocks, bar, notice, body)


@functools.lru_cache(maxsize=None)
def english() -> Doc:
    return parse(ENGLISH.read_text(encoding="utf-8"))


def translation(lang: str) -> Doc:
    path = ROOT / "READMEs" / f"README.{lang}.md"
    return parse(path.read_text(encoding="utf-8"))


def _excerpt(text: str, size: int = 90) -> str:
    text = " ".join(text.split())
    return text if len(text) <= size else text[: size - 3] + "..."


def _strip_tags(text: str) -> str:
    return html.unescape(TAG_RE.sub("", text)).replace("\u00a0", " ")


def targets(text: str) -> list[str]:
    """Every link and image target of a page, in order: html attributes and markdown links."""
    found = []
    for match in re.finditer(r'(?:href|src|srcset)="([^"]*)"|\]\(([^)\s]+)(?:\s+"[^"]*")?\)', text):
        found.append(match.group(1) if match.group(1) is not None else match.group(2))
    return [t for t in found if t]


def _kind(target: str) -> str:
    if re.match(r"https?://", target):
        return "absolute"
    if target.startswith("#"):
        return "anchor"
    return "relative"


def inline_code(text: str) -> list[str]:
    spans = []
    for line in text.split("\n"):
        if CODE_MARK in line:
            continue
        spans += re.findall(r"`([^`\n]+)`", line)
    return spans


def slug(heading: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text).replace("*", "")
    text = re.sub(r"[^\w\- ]", "", text.strip().lower(), flags=re.UNICODE)
    return text.replace(" ", "-")


def headings(outside: str) -> list[tuple[int, int, str]]:
    """(line index, level, text) of every heading, markdown and html, in page order."""
    found = []
    for match in re.finditer(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", outside, re.M):
        found.append((match.start(), len(match.group(1)), match.group(2)))
    for match in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", outside, re.S):
        found.append((match.start(), int(match.group(1)), _strip_tags(match.group(2)).strip()))
    found.sort()
    return [(outside[:pos].count("\n"), level, text) for pos, level, text in found]


def _cells(line: str) -> list[str]:
    protected = re.sub(r"`[^`]*`", lambda m: m.group(0).replace("|", "\u0001"), line.strip())
    cells = [c.replace("\u0001", "|").strip() for c in protected.split("|")]
    return cells[1:-1] if cells and cells[0] == "" and cells[-1] == "" else cells


def tables(body: str) -> list[list[list[str]]]:
    groups, current = [], []
    for line in body.split("\n"):
        if line.lstrip().startswith("|"):
            current.append(line)
        elif current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    result = []
    for group in groups:
        rows = [_cells(line) for line in group if not re.fullmatch(r"\|?[\s:\-|]+\|?", line.strip())]
        result.append(rows)
    return result


def numeric_tokens(text: str) -> list[str]:
    text = html.unescape(TAG_RE.sub(" ", text)).replace("\u00a0", " ").replace("**", "").replace("`", "")
    return [re.sub(r"\s", "", token) for token in NUMBER_RE.findall(text)]


def pictures(body: str) -> list[tuple[str, str, str]]:
    return [(m.group(1), m.group(2), html.unescape(m.group(3))) for m in PICTURE_RE.finditer(body)]


def prose_lines(body: str) -> list[str]:
    """Prose as a reader sees it: no code, no tables, no tags, no link targets."""
    lines = []
    for line in body.split("\n"):
        if line.lstrip().startswith("|") or CODE_MARK in line:
            continue
        text = html.unescape(TAG_RE.sub(" ", line)).replace("\u00a0", " ")
        text = re.sub(r"`[^`]*`", "", text)
        text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"^[#>\-*\d.\s]+", "", text).replace("*", "")
        text = " ".join(text.split())
        if len(re.findall(r"[^\W\d_]", text)) >= 3:
            lines.append(text)
    return lines


def _norm(line: str) -> str:
    return re.sub(r"[\s.,:;!?()\"'\u00a0]+", " ", line.casefold()).strip()


def language_bar(bar: str | None):
    """[(href or None, label)] in order. None means the entry is plain text."""
    if not bar:
        return []
    inner = re.sub(r"^<p\b[^>]*>|</p>\s*$", "", bar.strip()).replace("&lrm;", "").replace("&rlm;", "")
    entries = []
    for part in (p.strip() for p in inner.split("\u00b7")):
        link = re.fullmatch(r'<a href="([^"]*)">(.*?)</a>', part, re.S)
        if link:
            entries.append((link.group(1), _strip_tags(link.group(2)).strip()))
        else:
            entries.append((None, _strip_tags(part).strip()))
    return entries


def bar_codes(entries) -> list[str]:
    """The language code of each entry of the English bar, in order. The first entry is English."""
    codes = ["en"]
    for href, _ in entries[1:]:
        match = re.search(r"README\.([A-Za-z]{2}-[A-Za-z]{2})\.md", href or "")
        codes.append(match.group(1) if match else "?")
    return codes


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def _report(lang: str, rule: str, title: str, problems: list[str], hint: str) -> None:
    if not problems:
        return
    shown = "\n".join(f"  - {p}" for p in problems[:SHOWN])
    more = f"\n  ... and {len(problems) - SHOWN} more" if len(problems) > SHOWN else ""
    pytest.fail(
        f"READMEs/README.{lang}.md breaks rule {rule} ({title}):\n{shown}{more}\nHow to fix: {hint}",
        pytrace=False,
    )


def _run(lang: str, rule: str, title: str, hint: str, check) -> None:
    path = ROOT / "READMEs" / f"README.{lang}.md"
    if not path.is_file():
        pytest.fail(f"READMEs/README.{lang}.md does not exist. Write the translation there.", pytrace=False)
    try:
        problems = check(english(), translation(lang), lang)
    except Exception as error:  # a page so different that it cannot be read
        problems = [f"the file could not be checked ({type(error).__name__}: {error}). "
                    "It is probably far from the structure of README.md."]
    _report(lang, rule, title, problems, hint)


def _line_diff(expected: str, found: str) -> str:
    exp, got = expected.split("\n"), found.split("\n")
    for index in range(max(len(exp), len(got))):
        a = exp[index] if index < len(exp) else "<nothing>"
        b = got[index] if index < len(got) else "<nothing>"
        if a != b:
            return f"first difference at line {index + 1} of the block: expected {a!r}, found {b!r}"
    return "the blocks differ"


# --------------------------------------------------------------------------
# R01 code blocks
# --------------------------------------------------------------------------

def check_code_blocks(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    if len(en.blocks) != len(tr.blocks):
        problems.append(f"the page has {len(tr.blocks)} fenced code blocks, README.md has {len(en.blocks)}")
    for index, (a, b) in enumerate(zip(en.blocks, tr.blocks), 1):
        if a != b:
            what = f"info string {a[0]!r} became {b[0]!r}" if a[0] != b[0] else _line_diff(a[1], b[1])
            problems.append(f"code block {index} (the one that starts {_excerpt(a[1].split(chr(10))[0], 50)!r}) differs: {what}")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r01_fenced_code_blocks_are_byte_identical(lang):
    _run(lang, "R01", "fenced code blocks",
         "copy every ``` block from README.md exactly, in the same order, comments included. Never translate code.",
         check_code_blocks)


# --------------------------------------------------------------------------
# R02 inline code
# --------------------------------------------------------------------------

def check_inline_code(en: Doc, tr: Doc, lang: str) -> list[str]:
    a, b = Counter(inline_code(en.body)), Counter(inline_code(tr.body))
    problems = [f"missing inline code `{code}` (README.md has it {n} time(s), this page {b.get(code, 0)})"
                for code, n in (a - b).items()]
    problems += [f"inline code `{code}` is not in README.md (or appears more often than there)" for code in (b - a)]
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r02_inline_code_spans_are_the_same(lang):
    _run(lang, "R02", "inline code",
         "keep every `code span` of README.md exactly as it is, and do not add new ones.", check_inline_code)


# --------------------------------------------------------------------------
# R03 links
# --------------------------------------------------------------------------

def check_links(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    en_targets, tr_targets = targets(en.body), targets(tr.body)
    a = Counter(t for t in en_targets if _kind(t) == "absolute")
    b = Counter(t for t in tr_targets if _kind(t) == "absolute")
    problems += [f"missing absolute URL {url}" for url in (a - b)]
    problems += [f"absolute URL {url} is not in README.md" for url in (b - a)]
    expected = Counter("../" + t for t in en_targets if _kind(t) == "relative")
    found = Counter(t for t in tr_targets if _kind(t) == "relative")
    for target in (expected - found):
        original = target[3:]
        problems.append(f"relative link {original!r} must be {target!r} (add ../ in front; keep any #fragment as is)")
    for target in (found - expected):
        if not target.startswith("../"):
            problems.append(f"relative link {target!r} needs ../ in front (the file is one folder deeper than README.md)")
        else:
            problems.append(f"relative link {target!r} is not a link of README.md")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r03_links_keep_their_targets(lang):
    _run(lang, "R03", "links",
         "keep every http(s) URL as it is. Put ../ in front of every relative link and image path of README.md "
         "(INSTALL.md becomes ../INSTALL.md, assets/x.svg becomes ../assets/x.svg). Translate the link text only.",
         check_links)


# --------------------------------------------------------------------------
# R04 anchors
# --------------------------------------------------------------------------

def check_anchors(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    en_anchors = [t for t in targets(en.body) if _kind(t) == "anchor"]
    tr_anchors = [t for t in targets(tr.body) if _kind(t) == "anchor"]
    a, b = Counter(en_anchors), Counter(tr_anchors)
    problems += [f"missing in-page link {t} (README.md uses it {n} time(s))" for t, n in (a - b).items()]
    problems += [f"in-page link {t} is not used in README.md" for t in (b - a)]
    en_heads, tr_heads = headings(en.outside), headings(tr.outside)
    lines = tr.outside.split("\n")
    for target in dict.fromkeys(en_anchors):
        wanted = [i for i, (_, _, text) in enumerate(en_heads) if slug(text) == target[1:]]
        if not wanted:
            continue
        index = wanted[0]
        if index >= len(tr_heads):
            problems.append(f"no heading number {index + 1} for {target}")
            continue
        line_no = tr_heads[index][0]
        anchor = f'<a id="{target[1:]}"></a>'
        before = lines[line_no - 2] if line_no >= 2 else ""
        gap = lines[line_no - 1] if line_no >= 1 else ""
        if before.strip() != anchor or gap.strip() != "":
            problems.append(
                f'the heading that matches {target} (the translation of "{en_heads[index][2]}", line {line_no + 1}) must be '
                f'preceded by the line {anchor}, then one blank line (without the blank line the heading does not render)')
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r04_in_page_links_and_explicit_anchors(lang):
    _run(lang, "R04", "anchors",
         'keep the #targets of the links as they are. Translated headings get new automatic ids, so write '
         '<a id="install"></a> on its own line, then a blank line, then the translated heading, for every #target '
         "the page links to.", check_anchors)


# --------------------------------------------------------------------------
# R05 language bar
# --------------------------------------------------------------------------

def check_language_bar(en: Doc, tr: Doc, lang: str) -> list[str]:
    en_entries, tr_entries = language_bar(en.bar), language_bar(tr.bar)
    if not tr_entries:
        return ["the language bar is missing. It is the <p> that lists the 15 languages, as in README.md"]
    problems = []
    if len(tr_entries) != len(en_entries):
        problems.append(f"the language bar has {len(tr_entries)} entries, README.md has {len(en_entries)}. "
                        "Separate entries with ' · ' as README.md does")
        return problems
    for index, (code, (href, label)) in enumerate(zip(bar_codes(en_entries), tr_entries)):
        en_label = en_entries[index][1]
        if label != en_label:
            problems.append(f"entry {index + 1}: the name is {label!r}, it must stay {en_label!r} "
                            "(language names are written in their own language)")
        if code == "en":
            want = "../README.md"
        elif code == lang:
            want = None
        else:
            want = f"README.{code}.md"
        if href != want:
            if want is None:
                problems.append(f"entry {index + 1} ({label}) is this file's own language: write it as plain text, not a link")
            else:
                problems.append(f"entry {index + 1} ({label}) must link to {want!r}, it links to {href!r}")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r05_language_bar(lang):
    _run(lang, "R05", "language bar",
         "copy the bar of README.md. English links to ../README.md, the other languages link to their file name "
         "(README.es-ES.md), and the language of this file is plain text without a link.", check_language_bar)


# --------------------------------------------------------------------------
# R06 structure
# --------------------------------------------------------------------------

def _level_counts(levels: list[int]) -> str:
    return ", ".join(f"h{n}: {c}" for n, c in sorted(Counter(levels).items()))


def check_structure(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    en_levels = [level for _, level, _ in headings(en.outside)]
    tr_levels = [level for _, level, _ in headings(tr.outside)]
    if en_levels != tr_levels:
        problems.append(f"headings differ. README.md: {len(en_levels)} ({_level_counts(en_levels)}). "
                        f"This page: {len(tr_levels)} ({_level_counts(tr_levels)}). "
                        "Keep the same headings, at the same levels, in the same order")
    en_details, tr_details = len(re.findall(r"<details\b", en.body)), len(re.findall(r"<details\b", tr.body))
    if en_details != tr_details:
        problems.append(f"<details> blocks: README.md has {en_details}, this page has {tr_details}")
    en_summ = re.findall(r"<summary>(.*?)</summary>", en.body, re.S)
    tr_summ = re.findall(r"<summary>(.*?)</summary>", tr.body, re.S)
    if len(en_summ) == len(tr_summ):
        for a, b in zip(en_summ, tr_summ):
            if _norm(a) == _norm(b):
                problems.append(f"the <summary> {a!r} is not translated")
    else:
        problems.append(f"<summary> lines: README.md has {len(en_summ)}, this page has {len(tr_summ)}")
    en_tables, tr_tables = tables(en.body), tables(tr.body)
    if len(en_tables) != len(tr_tables):
        problems.append(f"tables: README.md has {len(en_tables)}, this page has {len(tr_tables)}")
    for index, (a, b) in enumerate(zip(en_tables, tr_tables), 1):
        first = _excerpt(" | ".join(a[0]), 60)
        if len(a) != len(b):
            problems.append(f"table {index} (header {first!r}) has {len(b)} rows, README.md has {len(a)}")
        elif any(len(x) != len(y) for x, y in zip(a, b)):
            row = next(i for i, (x, y) in enumerate(zip(a, b), 1) if len(x) != len(y))
            problems.append(f"table {index} (header {first!r}), row {row}: {len(b[row - 1])} cells, "
                            f"README.md has {len(a[row - 1])}")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r06_headings_details_and_tables_keep_their_structure(lang):
    _run(lang, "R06", "structure",
         "translate headings, <summary> lines and table text, but keep the same number of headings at each level, "
         "of <details> blocks, of tables, and of rows and cells in each table.", check_structure)


# --------------------------------------------------------------------------
# R07 images
# --------------------------------------------------------------------------

def check_images(en: Doc, tr: Doc, lang: str) -> list[str]:
    a, b = pictures(en.body), pictures(tr.body)
    problems = []
    if len(a) != len(b):
        return [f"<picture> blocks: README.md has {len(a)}, this page has {len(b)} (keep the block format of README.md; "
                "the alt text must not contain a double quote)"]
    for index, ((dark, light, alt), (tdark, tlight, talt)) in enumerate(zip(a, b), 1):
        label = f"picture {index} ({light})"
        if tdark != "../" + dark or tlight != "../" + light:
            problems.append(f"{label}: the paths must be ../{dark} and ../{light}, they are {tdark} and {tlight}")
        if numeric_tokens(alt) != numeric_tokens(talt):
            problems.append(f"{label}: the numbers of the alt text must be the same, in the same order. "
                            f"Expected {numeric_tokens(alt)}, found {numeric_tokens(talt)}")
        if _norm(alt) == _norm(talt):
            problems.append(f"{label}: the alt text is not translated")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r07_pictures_keep_their_paths_and_numbers(lang):
    _run(lang, "R07", "pictures",
         "keep each <picture> block as in README.md with ../assets/... paths. Translate the alt text, but keep every "
         "number and unit of it, in the same order. The pictures themselves stay in English.", check_images)


# --------------------------------------------------------------------------
# R08 numbers and names
# --------------------------------------------------------------------------

def _bold(cell: str) -> list[str]:
    return re.findall(r"\*\*(.+?)\*\*", cell)


ARROW = "\u2192"
LEFT_ARROW = "\u2190"
RTL_LANGS = ("ar-SA", "he-IL")


def _arrows(text: str) -> int:
    return text.count(ARROW) + text.count(LEFT_ARROW)


def _headline(doc: Doc) -> str:
    """The measured headline: the first bold paragraph with an arrow (the tagline above it has none)."""
    for match in PARA_RE.finditer(doc.outside):
        if "<b>" in match.group(0) and _arrows(match.group(0)):
            return match.group(0)
    return ""


def _prose_numbers(doc: Doc) -> Counter:
    """The numbers of the prose that a translator could localize by mistake: 4.9, 3,211, $0.0548, 375 MB, 3.15.0 ..."""
    found = Counter()
    for line in prose_lines(doc.body):
        for token in numeric_tokens(line):
            if re.search(r"[.,$]|MB|s$|%|\u00d7", token):
                found[token] += 1
    return found


def check_numbers(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    en_tables, tr_tables = tables(en.body), tables(tr.body)
    for t_index, (a, b) in enumerate(zip(en_tables, tr_tables), 1):
        for r_index, (x, y) in enumerate(zip(a, b), 1):
            first = _excerpt(" | ".join(x), 50)
            want, got = numeric_tokens(" | ".join(x)), numeric_tokens(" | ".join(y))
            if want != got:
                problems.append(
                    f"table {t_index}, row {r_index} ({first!r}): numbers differ. Expected {want}, found {got}. "
                    "Numbers, $, s, MB, % and the dash of a range are never localized")
            if [_bold(c) for c in x] != [_bold(c) for c in y]:
                problems.append(
                    f"table {t_index}, row {r_index} ({first!r}): the bold text differs. Bold marks the best value or an "
                    "agent supported in the matrix: keep **...** on the same cells and keep the bold text itself")
    # agent and product names: the last cell of each row of the agents table is a list of names
    for a, b in zip(en_tables, tr_tables):
        if any("Claude Code" in cell for row in a for cell in row):
            for x, y in list(zip(a, b))[1:]:  # the header row is translated; the names are not
                if x and y and x[-1] != y[-1]:
                    problems.append(f"agents table: the list of names {_excerpt(x[-1], 60)!r} must stay exactly as in "
                                    f"README.md, found {_excerpt(y[-1], 60)!r}")
    # the headline
    want, got = _headline(en), _headline(tr)
    if numeric_tokens(want) != numeric_tokens(got) or _arrows(want) != _arrows(got):
        problems.append(f"the headline (the bold line under the name): numbers or arrows differ. Expected {numeric_tokens(want)} "
                        f"with {_arrows(want)} arrows, found {numeric_tokens(got)} with {_arrows(got)}")
    # the arrows point the way the text is read: in a right-to-left paragraph an arrow to the right points from the second
    # value back to the first, and "121 s -> 25 s" reads as "25 s -> 121 s"
    expected, other = (LEFT_ARROW, ARROW) if lang in RTL_LANGS else (ARROW, LEFT_ARROW)
    if tr.raw.count(expected) != en.raw.count(ARROW) or tr.raw.count(other):
        problems.append(f"the page has {tr.raw.count(expected)} '{expected}' and {tr.raw.count(other)} '{other}'; README.md has "
                        f"{en.raw.count(ARROW)} '{ARROW}'. Write '{expected}' for each of them: the arrow must point the way "
                        f"the language is read ({'right to left' if lang in RTL_LANGS else 'left to right'})")
    # the prose
    for token, n in (_prose_numbers(en) - _prose_numbers(tr)).items():
        problems.append(f"the number {token!r} of README.md is missing in the prose (needed {n} time(s)). Keep numbers and "
                        "units as written: 3,211 stays 3,211, 4.9 stays 4.9")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r08_numbers_units_and_names_are_not_localized(lang):
    _run(lang, "R08", "numbers and names",
         "numbers, units ($, s, MB, %, ×), decimal points, thousands commas and en-dash ranges stay exactly as in "
         "README.md; the headline numbers too; the agent names in the agents table stay in English; "
         "bold stays on the same cells.",
         check_numbers)


# --------------------------------------------------------------------------
# R09 it is a translation
# --------------------------------------------------------------------------

def check_translated(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    en_lines, tr_lines = prose_lines(en.body), prose_lines(tr.body)
    long_tr = [line for line in tr_lines if len(line) >= SUBSTANTIAL_LINE]
    if len(long_tr) < 0.5 * len([line for line in en_lines if len(line) >= SUBSTANTIAL_LINE]):
        problems.append(f"the page has only {len(long_tr)} prose lines of {SUBSTANTIAL_LINE}+ characters, README.md has "
                        f"{len([line for line in en_lines if len(line) >= SUBSTANTIAL_LINE])}. Translate the whole page")
    english = {_norm(line) for line in en_lines if len(line) >= SUBSTANTIAL_LINE}
    same = [line for line in long_tr if _norm(line) in english]
    allowed = max(2, int(IDENTICAL_LINE_SHARE * max(len(long_tr), 1)))
    if len(same) > allowed:
        shown = "; ".join(repr(_excerpt(line, 60)) for line in same[:4])
        problems.append(f"{len(same)} prose lines are identical to English (at most {allowed} allowed, "
                        f"{int(IDENTICAL_LINE_SHARE * 100)}% of the long lines). Still English: {shown}")
    if lang in SCRIPT and long_tr:
        with_script = [line for line in long_tr if re.search(f"[{SCRIPT[lang]}]", line)]
        if len(with_script) < SCRIPT_LINE_SHARE * len(long_tr):
            lacking = [line for line in long_tr if line not in with_script][:3]
            problems.append(f"only {len(with_script)} of {len(long_tr)} long prose lines contain {lang} script (at least "
                            f"{int(SCRIPT_LINE_SHARE * 100)}% needed). Not translated, for example: "
                            + "; ".join(repr(_excerpt(line, 60)) for line in lacking))
    words = [w.casefold() for line in tr_lines for w in re.findall(r"[^\W\d_]+", line)]
    if words:
        share = sum(1 for w in words if w in ENGLISH_WORDS) / len(words)
        if share > ENGLISH_WORD_SHARE:
            problems.append(f"{share:.1%} of the words are English words such as 'the', 'and', 'with' "
                            f"(at most {ENGLISH_WORD_SHARE:.0%} allowed). Translate the remaining English prose")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r09_the_prose_is_translated(lang):
    _run(lang, "R09", "translated prose",
         f"translate every sentence. At most {int(IDENTICAL_LINE_SHARE * 100)}% of the lines of {SUBSTANTIAL_LINE}+ "
         "characters may equal an English line (product names, commands and file names are fine). "
         "Non-Latin languages must write their own script.",
         check_translated)


# --------------------------------------------------------------------------
# R10 right to left
# --------------------------------------------------------------------------

BIDI_CONTROLS = "\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"


def check_direction(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    # The convention of the current ar-SA and he-IL files: no explicit direction anywhere. GitHub sets the direction of
    # each paragraph from its first letters, and fenced code stays left to right.
    if re.search(r"\bdir\s*=|direction\s*:|<bdo\b", tr.raw, re.I):
        problems.append("the page sets a text direction (dir=, direction: or <bdo>). Do not: GitHub picks the direction of each "
                        "paragraph itself, and code blocks must stay left to right")
    if any(ch in tr.raw for ch in BIDI_CONTROLS):
        problems.append("the page contains an invisible direction-control character (RLM, LRE, RLE, PDF, LRO, RLO, LRI, RLI, "
                        "FSI, PDI). Remove it. Only the &lrm; entity after a right-to-left name in the language bar is allowed")
    for index, (_, content) in enumerate(tr.blocks, 1):
        if any(ch in content for ch in BIDI_CONTROLS):
            problems.append(f"code block {index} contains a direction-control character")
    if lang in ("ar-SA", "he-IL"):
        letters = SCRIPT[lang]
        if not re.search(f"[{letters}]", " ".join(prose_lines(tr.body))):
            problems.append(f"no {lang} text found in the prose")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r10_no_explicit_text_direction(lang):
    _run(lang, "R10", "text direction",
         "write the page the way the current ar-SA and he-IL files are written: no dir attribute, no direction style, "
         "no invisible direction characters. Code blocks must stay left to right.", check_direction)


# --------------------------------------------------------------------------
# R11 the translation notice
# --------------------------------------------------------------------------

def check_notice(en: Doc, tr: Doc, lang: str) -> list[str]:
    if tr.bar is None:
        return ["the language bar is missing, so the notice under it cannot be found"]
    if tr.notice is None:
        return ['there is no notice under the language bar. Add one <p align="center"><sub>...</sub></p> right after the '
                'language bar, with a link <a href="../README.md">...</a>']
    problems = []
    text = " ".join(_strip_tags(tr.notice).split())
    if len(text) < 40:
        problems.append(f"the notice is too short ({len(text)} characters): {text!r}")
    if lang in SCRIPT and not re.search(f"[{SCRIPT[lang]}]", text):
        problems.append(f"the notice is not written in {lang} script: {text!r}")
    if re.search(r"This (?:page )?is a translation", text, re.I):
        problems.append("the notice is still English")
    first_picture = tr.outside.find("<picture>")
    if first_picture != -1 and tr.outside.find(tr.notice) > first_picture:
        problems.append("the notice must come right after the language bar, before the first picture")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r11_translation_notice_under_the_language_bar(lang):
    _run(lang, "R11", "translation notice",
         'right after the language bar add <p align="center"><sub>...</sub></p>. In the language of the file it says: this is '
         "a translation of the English README (the words 'English README' are the link <a href=\"../README.md\">), the English "
         "page is the reference if they differ, and the figures are in English.", check_notice)


# --------------------------------------------------------------------------
# R12 claims that were removed
# --------------------------------------------------------------------------

def check_removed_claims(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    raw = tr.raw
    for needle in REMOVED_STRINGS:
        if needle in raw:
            problems.append(f"the old text {needle!r} is still in the page. README.md no longer says it: remove it")
    for pattern in REMOVED_PATTERNS:
        if re.search(pattern, raw):
            problems.append(f"the old text {pattern!r} (a package manager command) is still in the page: remove it")
    # 3.10.8 belongs to the one sentence about the older script benchmark, and only there.
    if raw.count("3.10.8") != en.raw.count("3.10.8"):
        problems.append(f"'3.10.8' appears {raw.count('3.10.8')} time(s), README.md has it {en.raw.count('3.10.8')} time(s) "
                        "(only in the bullet about the older Python-script benchmark)")
    for target in targets(tr.body):
        if re.fullmatch(r"(?:\.\./)?benchmarks/?", target):
            problems.append(f"the link {target!r} points at the benchmarks folder. "
                            "README.md links only the 2026-11-22 report and its JSON")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r12_claims_of_the_old_pages_are_gone(lang):
    _run(lang, "R12", "removed claims",
         "the old pages had benchmark tables, size and speed claims, other install tools and a folder link that README.md "
         "dropped. Translate README.md only and delete everything else of the old file.", check_removed_claims)


# --------------------------------------------------------------------------
# R13 strings that other tests pin
# --------------------------------------------------------------------------

def check_pinned(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = [f"the string {needle!r} must be in the page (other tests pin it)" for needle in PINNED if needle not in tr.raw]
    problems += [f"the string {needle!r} must not be in the page" for needle in ("SIMPLICIO_INSTALL_CODEX", "HTTP/OAuth")
                 if needle in tr.raw]
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r13_strings_pinned_by_other_tests(lang):
    _run(lang, "R13", "pinned strings",
         "the install commands come from the code blocks of README.md; copy them exactly (see R01).", check_pinned)


# --------------------------------------------------------------------------
# R14 the brand line
# --------------------------------------------------------------------------

def check_tagline(en: Doc, tr: Doc, lang: str) -> list[str]:
    problems = []
    lines = tr.raw.split("\n")
    if lines.count(TAGLINE) != 1:
        return [f"the line {TAGLINE} must appear exactly once, unchanged and in English "
                f"(it appears {lines.count(TAGLINE)} times)"]
    index = lines.index(TAGLINE)
    if index < 2 or lines[index - 2] != "<h1>Simplicio</h1>" or lines[index - 1] != "":
        problems.append("the tagline goes right under <h1>Simplicio</h1>, with one blank line between them")
    if (index + 2 >= len(lines) or not (ARROW in lines[index + 2] or LEFT_ARROW in lines[index + 2])
            or not lines[index + 2].startswith("<p><b>")):
        problems.append("the measured headline (<p><b>... 121 s → 25 s ...</b></p>) follows the tagline after one blank line")
    if tr.raw.count("UltraFast") != 1:
        problems.append("the word UltraFast appears outside the tagline. The brand line is never translated or repeated")
    return problems


@pytest.mark.parametrize("lang", LANGS)
def test_r14_the_tagline_is_the_same_english_brand_line(lang):
    _run(lang, "R14", "tagline",
         f"right under <h1>Simplicio</h1> keep the line {TAGLINE} exactly as in README.md. "
         "It is a brand line: never translate it.",
         check_tagline)
