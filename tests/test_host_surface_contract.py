from __future__ import annotations

import ast
import json
from pathlib import Path

from simplicio.host_integrations import HOSTS


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "host-surface-v1.json"
HERMES = ROOT / "plugins" / "simplicio-hermes" / "hermes_plugin.py"
PLUGIN_MANIFEST = ROOT / "plugins" / "simplicio" / ".claude-plugin" / "plugin.json"
MCP_MANIFEST = ROOT / "plugins" / "simplicio" / ".mcp.json"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _hermes_mapper_tools() -> set[str]:
    tree = ast.parse(HERMES.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_MAPPER_TOOLS":
                    return {elt.value for elt in node.value.args[0].elts}
    raise AssertionError("Hermes _MAPPER_TOOLS not found")


def test_host_surface_fixture_matches_claude_and_full_mode_contracts() -> None:
    surface = _fixture()
    claude = next(spec for spec in HOSTS if spec.host_id == "claude-code")
    cursor = next(spec for spec in HOSTS if spec.host_id == "cursor")
    forbidden = set(surface["modes"]["mapper-only"]["forbidden"])
    retired = set(surface["retired_aliases"])

    assert surface["schema"] == "simplicio.host-surface/v1"
    assert surface["cli"] == [
        "simplicio map",
        "simplicio context",
        "simplicio memory",
        "simplicio edit",
        "simplicio run",
    ]
    assert claude.mcp_environment == (("SIMPLICIO_RUNTIME_MODE", "mapper-only"),)
    assert cursor.mcp_environment == ()
    assert forbidden.isdisjoint(surface["modes"]["mapper-only"]["tools"])
    assert retired.isdisjoint(surface["modes"]["mapper-only"]["tools"])
    assert retired.isdisjoint(surface["modes"]["full"]["canonical"])


def test_opencode_host_surface_is_native_plugin_with_full_mode() -> None:
    surface = _fixture()
    package = json.loads(
        (ROOT / "plugins" / "simplicio" / "host-surfaces.json").read_text(encoding="utf-8")
    )
    entry = next(host for host in package["hosts"] if host["id"] == "opencode")
    opencode = next(spec for spec in HOSTS if spec.host_id == "opencode")
    full_hosts = set(surface["modes"]["full"]["hosts"])
    canonical = set(surface["modes"]["full"]["canonical"])

    assert entry["surface"] == "native-plugin"
    assert entry["manifest"] == "opencode.json"
    assert entry["preHooks"] == "runtime-managed"
    assert "opencode" in full_hosts
    assert {"simplicio_edit", "simplicio_run", "simplicio_map", "simplicio_context"} <= canonical
    assert opencode.capability == "native-plugin"
    assert ("SIMPLICIO_RUNTIME_MODE", "full") in opencode.mcp_environment
    assert "opencode" not in set(surface["modes"]["mapper-only"]["hosts"])


def test_hermes_mapper_only_surface_excludes_execution_tools() -> None:
    surface = _fixture()
    tools = _hermes_mapper_tools()
    forbidden = set(surface["modes"]["mapper-only"]["forbidden"])
    retired = set(surface["retired_aliases"])
    assert "simplicio_map" in tools
    assert "simplicio_context" in tools
    assert tools.isdisjoint(forbidden)
    assert tools.isdisjoint(retired)


def test_plugin_manifests_do_not_start_a_competing_mapper_engine() -> None:
    plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    mcp = json.loads(MCP_MANIFEST.read_text(encoding="utf-8"))
    command = json.dumps(mcp)
    assert plugin["keywords"] == [
        "simplicio",
        "mcp",
        "mapper-only",
        "project-map-cache",
        "local-first",
        "validation",
    ]
    assert "simplicio-mapper" not in command
    assert "code-graph" not in command
    assert "mapper-foreground" not in command
    assert "mcpServers" in plugin
