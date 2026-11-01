#!/usr/bin/env python3
"""Functional check of a delivered users.html, in headless Chrome, outside the session metrics.

The page is exercised the way a person would: it must list every row, search, sort and, after the
edit phase, filter with a counter that respects the search and the filter together. Works on any
page structure a model or a generator produces; it never reads a specific markup.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
RESULT_ID = "__bench_check__"


@dataclass
class PageSpec:
    """What the delivered page must do with its data."""

    values: list  # one distinct value per row; all of them must be visible
    search_term: str  # matches some rows, not all
    sort_header: str  # the column header to click
    filter_value: str  # the option to pick
    filter_rows: int  # rows left after picking it
    connector: str  # the counter's word: "X de Y" or "X of Y"

PROBE = r"""<script>
window.addEventListener('load', async () => {
  const out = {};
  const SPEC = __SPEC__;
  const wait = (ms = 80) => new Promise((resolve) => setTimeout(resolve, ms));
  const rows = () => [...document.querySelectorAll('tbody tr')].filter((row) => row.offsetParent !== null);
  const text = () => document.body.innerText;
  const fire = (element, value) => {
    element.value = value;
    for (const type of ['input', 'keyup', 'change']) element.dispatchEvent(new Event(type, { bubbles: true }));
  };
  try {
    await wait(250);
    out.rows = rows().length;
    out.all_values = SPEC.values.every((value) => text().includes(value));
    const search = document.querySelector('input[type=search], input[type=text], input:not([type])');
    out.has_search = Boolean(search);
    if (search) {
      fire(search, SPEC.search_term);
      await wait();
      out.search_rows = rows().length;
      fire(search, '');
      await wait();
    }
    const headers = [...document.querySelectorAll('th')];
    const nameHeader = headers.find((header) => new RegExp(SPEC.sort_header, 'i').test(header.innerText)) || headers[0];
    const target = nameHeader && (nameHeader.querySelector('button, a') || nameHeader);
    const first = () => (rows()[0] ? rows()[0].innerText : '');
    if (target) {
      const before = first();
      target.click();
      await wait();
      const once = first();
      target.click();
      await wait();
      out.sort_changes = new Set([before, once, first()]).size > 1;
    }
    const matches = (value) => new RegExp(SPEC.filter_value, 'i').test(value || '');
    const select = [...document.querySelectorAll('select')].find((item) => [...item.options].some((option) => matches(option.textContent + ' ' + option.value)));
    let activate = null;
    if (select) {
      const option = [...select.options].find((item) => matches(item.textContent + ' ' + item.value));
      activate = () => fire(select, option.value);
    } else {
      const control = [...document.querySelectorAll('button, label, input[type=radio], a, [role=tab], [role=radio]')].find((item) => matches(item.textContent || item.value));
      if (control) activate = () => control.click();
    }
    out.has_filter = Boolean(activate);
    if (activate) {
      activate();
      await wait();
      out.filter_rows = rows().length;
      out.filter_only_inactive = rows().every((row) => matches(row.innerText));
      out.counter_filter = new RegExp('\\b' + SPEC.filter_rows + '\\s+' + SPEC.connector + '\\s+' + SPEC.values.length + '\\b').test(text());
      if (search) {
        fire(search, 'a');
        await wait();
        const shown = rows().length;
        out.combined_rows = shown;
        out.counter_combined = new RegExp('\\b' + shown + '\\s+' + SPEC.connector + '\\s+' + SPEC.values.length + '\\b').test(text());
      }
    }
  } catch (error) {
    out.error = String(error);
  }
  const result = document.createElement('pre');
  result.id = '__RESULT_ID__';
  result.textContent = JSON.stringify(out);
  document.body.appendChild(result);
});
</script>"""


def external_refs(html: str) -> list[str]:
    refs = re.findall(r"<script[^>]+\bsrc=[^>]*>|<link[^>]+\bhref=[^>]*>|<img[^>]+\bsrc=[^>]*>", html, re.I)
    refs += [url for url in re.findall(r"https?://[^\s\"'<>)]+", html) if "w3.org" not in url]
    return refs[:5]


def browser_probe(html: str, spec: PageSpec) -> dict:
    probe = PROBE.replace("__SPEC__", json.dumps(asdict(spec))).replace("__RESULT_ID__", RESULT_ID)
    marker = html.lower().rfind("</body>")
    instrumented = (html[:marker] + probe + html[marker:]) if marker >= 0 else html + probe
    with tempfile.TemporaryDirectory(prefix="bench-check-") as tmp:
        page = Path(tmp) / "page.html"
        page.write_text(instrumented)
        try:
            done = subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                 "--user-data-dir=" + str(Path(tmp) / "profile"), "--virtual-time-budget=8000",
                 "--dump-dom", page.as_uri()],
                capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            return {"error": "chrome timeout"}
    found = re.search(r'id="%s">(.*?)</pre>' % RESULT_ID, done.stdout, re.S)
    if not found:
        return {"error": "probe did not finish", "stderr": done.stderr[-200:]}
    body = found.group(1).replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return json.loads(body)


def check(page: Path, spec: PageSpec, edited: bool) -> dict:
    """`ok` needs the listing, search and sort; after the edit also the filter and both counters."""
    if not page.exists():
        return {"ok": False, "exists": False}
    html = page.read_text(errors="replace")
    result = browser_probe(html, spec)
    result["exists"] = True
    result["bytes"] = len(html)
    result["external_refs"] = external_refs(html)
    listing = (
        result.get("rows") == len(spec.values)
        and result.get("all_values") is True
        and 1 <= result.get("search_rows", 0) < len(spec.values)
        and result.get("sort_changes") is True
        and not result["external_refs"]
    )
    filtered = (
        result.get("filter_rows") == spec.filter_rows
        and result.get("filter_only_inactive") is True
        and result.get("counter_filter") is True
        and result.get("counter_combined") is True
    )
    result["ok"] = bool(listing and (filtered or not edited))
    return result
