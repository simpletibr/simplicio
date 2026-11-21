"""The guides and lists of the twelve harnesses of the Runtime bot study.

The Runtime writes a file for four of them and nothing for the other eight, and
none was run against a real installation of its product, so every public text
says what the Runtime writes or prints, keeps its UNVERIFIED marks, and does not
claim support for a Runtime that may not list the id yet.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "pypi" / "simplicio"))

from simplicio.host_integrations import HOSTS, compatibility_matrix  # noqa: E402

HOSTS_DIR = ROOT / "docs" / "hosts"
WRITTEN = ("grok", "muse-code", "openmausbot", "openmuse")
ROUTE_ONLY = ("opendots", "openbot", "agentes-chat", "dots", "grok-bot", "muse", "cue")
DELEGATING = ("t3-code",)
ALL = WRITTEN + ROUTE_ONLY + DELEGATING


def _page(host_id: str) -> str:
    return (HOSTS_DIR / f"{host_id}.md").read_text(encoding="utf-8")


def _doc(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_every_harness_has_one_page_that_says_it_needs_a_runtime_that_lists_it() -> None:
    assert len(ALL) == 12
    for host_id in ALL:
        text = _page(host_id)
        assert text.startswith("# Simplicio with "), host_id
        needs = f"Needs a Simplicio Runtime that lists `{host_id}` in `simplicio integrate list`."
        assert needs in text, host_id
        # No version of the Runtime is named: the release that carries the ids is not cut yet.
        assert not re.search(r"Runtime v?\d", text), host_id
        assert not re.search(r"\b(is|are) (now |fully )?supported\b", text), host_id


def test_every_page_keeps_its_unverified_marks_and_says_nothing_was_run() -> None:
    for host_id in ALL:
        text = _page(host_id)
        assert "## Not verified" in text, host_id
        assert "UNVERIFIED" in text, host_id
        assert re.search(
            r"was not run against a real|Nothing was run against|None of this was run against",
            text,
        ), host_id
        assert "## Sources" in text, host_id


def test_pages_name_no_private_path_and_no_local_command() -> None:
    for host_id in ALL:
        text = _page(host_id)
        assert "/home/" not in text and "git -C" not in text, host_id
        assert "simplicio-runtime" not in text, host_id


def test_pages_of_the_four_writers_state_the_rules_of_the_writer() -> None:
    config = {
        "grok": "~/.grok/config.toml",
        "muse-code": "~/.config/muse/settings.json",
        "openmausbot": "~/.openmausbot/config.json",
        "openmuse": "~/.openmuse/config.toml",
    }
    for host_id in WRITTEN:
        text = _page(host_id)
        assert f"simplicio integrate install --host {host_id}" in text, host_id
        assert config[host_id] in text, host_id
        # A plain rule, not a hedge: the Runtime tests all four.
        assert "refused and left byte for byte as it was" in text, host_id
        assert "A second run changes nothing." in text, host_id
        assert "removes only" in text, host_id
        assert "The sources do not say how the Runtime" not in text, host_id
        assert f"simplicio integrate verify --host {host_id}" in text, host_id
    assert "resultBudget" in _page("openmausbot")
    assert '"schema_version": 1' in _page("muse-code")
    assert "[[mcp.servers]]" in _page("openmuse")
    assert "[mcp_servers.simplicio]" in _page("grok")


def test_pages_of_the_other_eight_write_nothing_and_name_the_command() -> None:
    for host_id in ROUTE_ONLY:
        text = _page(host_id)
        assert f"simplicio integrations routes {host_id}" in text, host_id
        assert "writes nothing" in text, host_id
    t3 = _page("t3-code")
    assert "Simplicio writes nothing for T3 Code" in t3
    assert "simplicio integrate verify --host t3-code" in t3
    assert "simplicio mcp register" in t3
    # The product is agentes.chat, with an e; the site agents.chat is another one.
    assert "spelled with an e" in _page("agentes-chat")
    assert "different site" in _page("agentes-chat")


def test_the_index_links_every_page() -> None:
    index = _doc("docs/README.md")
    for host_id in ALL:
        assert f"](hosts/{host_id}.md)" in index, host_id
    assert "twelve harnesses of the Runtime bot study" in index


def _matrix_rows() -> dict[str, tuple[str, str, str]]:
    rows = {}
    for line in _doc("docs/hosts/compatibility-matrix.md").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 4 and not set(cells[0]) <= {"-", " "} and cells[0] != "Host":
            rows[cells[0]] = (cells[1], cells[2], cells[3])
    return rows


def test_compatibility_matrix_document_matches_the_code_for_the_twelve() -> None:
    rows = _matrix_rows()
    by_id = {spec.host_id: spec for spec in HOSTS}
    matrix = {row["id"]: row for row in compatibility_matrix()}
    for host_id in ALL:
        spec = by_id[host_id]
        probe = ", ".join(f"`{name}`" for name in spec.executable_names) or "—"
        assert rows[spec.name] == (
            matrix[host_id]["capability"],
            matrix[host_id]["contract"],
            probe,
        ), host_id


def test_installer_paths_document_lists_the_four_files_and_the_eight_routes() -> None:
    text = _doc("docs/INSTALLER_HOSTS.md")
    by_id = {spec.host_id: spec for spec in HOSTS}
    for host_id in WRITTEN:
        assert f"hosts/{host_id}.md" in text, host_id
        for path in by_id[host_id].config_paths:
            assert f"`{path}`" in text, (host_id, path)
    for host_id in ROUTE_ONLY + DELEGATING:
        assert f"(hosts/{host_id}.md)" in text, host_id
    assert "`nothing_written`" in text
    assert "an older Runtime download does not gain it from this page" in text


def test_no_public_text_still_describes_grok_as_the_superagent_cli() -> None:
    for relative in (
        "docs/INSTALLER_HOSTS.md",
        "docs/hosts/compatibility-matrix.md",
        "docs/HOST_INTEGRATIONS.md",
        "plugins/simplicio/README.md",
        "plugins/simplicio/host-surfaces.json",
        "pypi/simplicio/simplicio/host_integrations.py",
    ):
        text = _doc(relative)
        assert "Grok CLI (Superagent)" not in text, relative
        assert "superagent-ai" not in text, relative


def test_plugin_readme_states_the_number_of_hosts_the_registry_lists() -> None:
    import json

    registry = json.loads(_doc("plugins/simplicio/host-surfaces.json"))
    ids = {host["id"] for host in registry["hosts"]}
    readme = " ".join(_doc("plugins/simplicio/README.md").split())
    match = re.search(r"surface of each of the (\d+) host ids it lists", readme)
    assert match, "the README must state how many host ids host-surfaces.json lists"
    assert int(match.group(1)) == len(ids)
    for host_id in ("muse-code", "openmausbot", "openmuse", "t3-code", "opendots", "openbot",
                    "agentes-chat", "dots", "grok-bot", "muse", "cue", "grok"):
        assert f"`{host_id}`" in readme, host_id
        assert host_id in ids
