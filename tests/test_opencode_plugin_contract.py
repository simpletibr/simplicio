"""Contract for the managed OpenCode plugin (#450).

The npm package ``opencode-simplicio`` never resolved. A bare local ``.js``
file is also rejected by OpenCode V2 ("configured plugin path must be a
directory"), and the V1 async-function export is rejected by the V2 loader
("Plugin must export a default definition with an id and an effect or setup
function"). The public contract therefore ships a managed plugin directory with
a V2 ``setup`` entrypoint (plus the V1 ``server`` fallback) and declares that
directory under ``plugins``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins"
MANIFEST = PLUGIN_ROOT / "simplicio" / "opencode.json"
PACKAGE = PLUGIN_ROOT / "simplicio" / "opencode"
DOC = ROOT / "docs" / "hosts" / "opencode.md"
PLUGIN_MANIFEST = PLUGIN_ROOT / "simplicio" / "plugin.json"

MANAGED_PLUGIN = "~/.simplicio/hooks/opencode-simplicio"
NPM_PLUGIN = "opencode-simplicio"
NATIVE_ROUTES = {
    "read": "simplicio_file",
    "write": "simplicio_edit",
    "edit": "simplicio_edit",
    "shell": "simplicio_exec",
}


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


def test_opencode_manifest_declares_a_managed_v2_plugin_directory() -> None:
    manifest = _manifest()
    plugin = manifest["plugin"]

    assert isinstance(plugin, str)
    normalized = plugin.replace("\\", "/")
    assert normalized == MANAGED_PLUGIN
    assert normalized != NPM_PLUGIN
    assert manifest["configKey"] == "plugins"
    assert manifest["pluginKind"] == "directory"
    assert manifest["pluginApi"] == "opencode-v2"
    assert manifest["pluginEntry"] == "index.js"
    assert manifest["pluginSource"] == "opencode/"
    assert "pluginRepository" not in manifest

    environment = manifest["mcp"]["environment"]
    assert environment["SIMPLICIO_RUNTIME_MODE"] == "full"
    assert environment["SIMPLICIO_MCP_PROFILE"] == "full"
    for tool, governed in NATIVE_ROUTES.items():
        assert manifest["nativeToolRoutes"][tool] == governed


def test_managed_plugin_package_is_loadable_by_opencode_v2() -> None:
    package = json.loads((PACKAGE / "package.json").read_text(encoding="utf-8"))
    source = (PACKAGE / "index.js").read_text(encoding="utf-8")
    version = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))["version"]

    assert package["name"] == NPM_PLUGIN  # V1 host identity, not an npm install reference
    assert package["version"] == version
    assert package["type"] == "module"
    assert package["private"] is True
    assert package["exports"] == {".": "./index.js"}

    assert 'id: "simplicio"' in source
    assert "async setup(ctx)" in source
    assert 'hook.call(ctx.tool, "execute.before"' in source
    assert "async server()" in source
    assert "NATIVE_TOOL_ROUTES" in source
    assert 'shell: "simplicio_exec"' in source


def test_docs_describe_the_v2_directory_repair_and_verification() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "execute.before" in text
    assert "opencode-v2" in text
    assert "directory" in text.lower()
    assert "scripts/opencode_plugin.py" in text
    assert "simplicio integrate verify --host opencode" in text
    assert MANAGED_PLUGIN in text
    for tool in ("simplicio_file", "simplicio_edit", "simplicio_exec"):
        assert tool in text
    assert "third-party" in text.lower()
    assert "final gate" in text.lower()
    assert "Pasblinn/opencode-simplicio" not in text


def test_no_public_manifest_keeps_an_npm_install_reference() -> None:
    manifests = sorted(PLUGIN_ROOT.rglob("*.json"))
    assert manifests

    offenders: list[str] = []
    for path in manifests:
        document = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(ROOT).as_posix()
        own_name = path.name == "package.json" and document.get("name") == NPM_PLUGIN
        for value in _walk(document):
            if value == NPM_PLUGIN and not own_name:
                offenders.append(relative)
            if isinstance(value, dict) and value.get("package") == NPM_PLUGIN:
                offenders.append(relative)

    manifest = _manifest()
    assert NPM_PLUGIN not in _walk(manifest)
    assert offenders == []
