from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_official_mcp_registry_entry_is_publishable_and_matches_the_release():
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    version = (ROOT / "version.txt").read_text(encoding="utf-8").strip()
    assert server["name"] == "io.github.simpletibr/simplicio"
    assert server["repository"]["url"] == "https://github.com/simpletibr/simplicio"
    assert server["version"] == version
    package = server["packages"][0]
    assert package["registryType"] == "npm"
    assert package["identifier"] == "@simpletibr/simplicio"
    assert package["version"] == version
    assert package["transport"]["type"] == "stdio"
    # The registry runs `<bin> <packageArguments>`; with no arguments the
    # launcher prints usage text instead of speaking MCP over stdio.
    assert package["packageArguments"] == [
        {"type": "positional", "value": "serve"},
        {"type": "named", "name": "--mcp"},
        {"type": "named", "name": "--stdio"},
        {"type": "named", "name": "--no-facade-mode"},
    ]
    command_line = [
        argument["value"] if argument["type"] == "positional" else argument["name"]
        for argument in package["packageArguments"]
    ]
    assert command_line == ["serve", "--mcp", "--stdio", "--no-facade-mode"]
    # The registry only accepts an npm entry whose package.json carries an
    # mcpName equal to the entry's name, and the entry must point at that package.
    wrapper = json.loads((ROOT / "npm/simplicio/package.json").read_text(encoding="utf-8"))
    assert package["identifier"] == wrapper["name"]
    assert wrapper["mcpName"] == server["name"]
    # The registry rejects a description longer than 100 characters.
    assert 1 <= len(server["description"]) <= 100


def test_each_host_channel_documents_one_command_install():
    claude = (ROOT / "PLUGIN.md").read_text(encoding="utf-8")
    codex = (ROOT / "docs/hosts/codex.md").read_text(encoding="utf-8")
    cursor = (ROOT / "docs/hosts/cursor.md").read_text(encoding="utf-8")
    gemini = (ROOT / "PLUGIN.md").read_text(encoding="utf-8")
    assert "/plugin marketplace add simpletibr/simplicio" in claude
    assert "codex plugin marketplace add simpletibr/simplicio" in codex
    assert "plugins/simplicio" in cursor
    assert "gemini extensions install" in gemini


def test_marketplace_entries_point_at_existing_packages():
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert marketplace["name"] == "simplicio"
    names = {entry["name"] for entry in marketplace["plugins"]}
    assert {"simplicio", "simplicio-loop", "simplicio-prompt", "simplicio-hermes"} <= names
    for entry in marketplace["plugins"]:
        source = entry["source"].removeprefix("./")
        assert (ROOT / source).exists(), entry
