"""Contract for the managed OpenCode plugin (#450).

The npm package ``opencode-simplicio`` never resolved. Runtime now installs
``~/.simplicio/hooks/opencode-simplicio.js`` and registers that local file, so
the public manifest and docs must describe the managed file instead of the npm
name.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins"
MANIFEST = PLUGIN_ROOT / "simplicio" / "opencode.json"
DOC = ROOT / "docs" / "hosts" / "opencode.md"

MANAGED_PLUGIN = "~/.simplicio/hooks/opencode-simplicio.js"
NPM_PLUGIN = "opencode-simplicio"


def _manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def test_opencode_manifest_declares_the_managed_local_plugin_file() -> None:
    manifest = _manifest()
    plugin = manifest["plugin"]

    assert isinstance(plugin, str)
    normalized = plugin.replace("\\", "/")
    assert normalized == MANAGED_PLUGIN or normalized.endswith(
        "/.simplicio/hooks/opencode-simplicio.js"
    )
    assert normalized != NPM_PLUGIN
    assert "pluginRepository" not in manifest

    environment = manifest["mcp"]["environment"]
    assert environment["SIMPLICIO_RUNTIME_MODE"] == "full"
    assert environment["SIMPLICIO_MCP_PROFILE"] == "full"


def test_docs_describe_enforcement_repair_and_verification() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "tool.execute.before" in text
    assert "integrate verify --host opencode" in text
    assert MANAGED_PLUGIN in text
    for tool in ("simplicio_file", "simplicio_edit", "simplicio_exec"):
        assert tool in text
    assert "third-party" in text.lower()
    assert "final gate" in text.lower()
    assert "Pasblinn/opencode-simplicio" not in text


def test_no_public_manifest_keeps_the_npm_plugin_reference() -> None:
    manifests = sorted(PLUGIN_ROOT.rglob("*.json"))
    assert manifests

    offenders: list[str] = []
    for path in manifests:
        document = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(ROOT).as_posix()
        for value in _walk(document):
            if value == NPM_PLUGIN:
                offenders.append(relative)
            if isinstance(value, dict) and value.get("package") == NPM_PLUGIN:
                offenders.append(relative)

    assert offenders == []
