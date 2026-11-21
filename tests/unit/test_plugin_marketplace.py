"""Contract tests for the public Simplicio marketplace bundle."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_marketplace_lists_existing_plugins() -> None:
    marketplace = _load_json(".claude-plugin/marketplace.json")
    assert marketplace["name"] == "simplicio"
    assert [entry["name"] for entry in marketplace["plugins"]] == [
        "simplicio",
        "simplicio-loop",
        "simplicio-prompt",
        "simplicio-hermes",
    ]
    assert not (ROOT / "plugins/simplicio-sprint").exists()

    for entry in marketplace["plugins"]:
        source = ROOT / entry["source"]
        assert (source / ".claude-plugin/plugin.json").is_file()
        assert (source / "LICENSE").is_file()


def test_plugin_manifests_have_skill_sources() -> None:
    marketplace = _load_json(".claude-plugin/marketplace.json")

    for entry in marketplace["plugins"]:
        source = ROOT / entry["source"]
        manifest = _load_json(str(Path(entry["source"]) / ".claude-plugin/plugin.json"))
        skills = manifest["skills"]
        skill_paths = [skills] if isinstance(skills, str) else skills
        assert skill_paths
        for skill_path in skill_paths:
            skill_dir = source / skill_path.removeprefix("./")
            assert any(skill_dir.rglob("SKILL.md"))


def test_codex_marketplace_packages_simplicio_plugin() -> None:
    marketplace = _load_json(".agents/plugins/marketplace.json")
    assert marketplace["name"] == "simplicio-codex"

    entry = marketplace["plugins"][0]
    assert entry["name"] == "simplicio"
    source = ROOT / entry["source"]["path"]
    manifest = json.loads(
        (source / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )

    assert manifest["name"] == entry["name"]
    assert manifest["mcpServers"] == "./.mcp.json"
    assert (source / "bin/simplicio-mcp-bootstrap.js").is_file()
    assert (source / "assets/simplicio-logo.png").is_file()
    assert (source / "LICENSE").is_file()
    assert any((source / "skills").rglob("SKILL.md"))



def test_portable_agent_plugin_contract() -> None:
    source = ROOT / "plugins/simplicio"
    manifest = _load_json("plugins/simplicio/plugin.json")
    mcp = _load_json("plugins/simplicio/mcp.json")

    assert manifest["$schema"].endswith("/1.0.0/plugin.schema.json")
    assert manifest["name"] == "simplicio"
    assert mcp["$schema"].endswith("/1.0.0/mcp.schema.json")
    server = mcp["mcpServers"]["simplicio-runtime"]
    assert server["type"] == "stdio"
    assert server["command"] == "node"
    assert server["cwd"] == "${PLUGIN_ROOT}"
    assert (source / server["args"][0].removeprefix("./")).is_file()


def test_native_claude_and_gemini_manifests_use_their_host_bootstrap() -> None:
    claude = _load_json("plugins/simplicio/.claude-plugin/plugin.json")
    gemini = _load_json("plugins/simplicio/gemini-extension.json")

    assert claude["name"] == gemini["name"] == "simplicio"
    assert claude["mcpServers"] == "./.mcp.json"
    claude_mcp = _load_json("plugins/simplicio/.mcp.json")
    assert claude_mcp["mcpServers"]["simplicio-runtime"]["args"] == [
        "./bin/simplicio-claude-mcp-bootstrap.js"
    ]
    args = gemini["mcpServers"]["simplicio-runtime"]["args"]
    assert args == ["${extensionPath}/bin/simplicio-mcp-bootstrap.js"]


def test_simplicio_plugin_manifests_share_one_version() -> None:
    manifests = [
        _load_json("plugins/simplicio/plugin.json"),
        _load_json("plugins/simplicio/.codex-plugin/plugin.json"),
        _load_json("plugins/simplicio/.claude-plugin/plugin.json"),
        _load_json("plugins/simplicio/gemini-extension.json"),
    ]

    assert {manifest["version"] for manifest in manifests} == {manifests[0]["version"]}


def test_hermes_plugin_manifests_share_one_version() -> None:
    manifests = [
        _load_json("plugins/simplicio-hermes/.claude-plugin/plugin.json"),
        _load_json("plugins/simplicio-hermes/manifest.json"),
        _load_json("plugins/simplicio-hermes/package.json"),
    ]

    assert {manifest["version"] for manifest in manifests} == {"0.4.0"}


def test_public_install_docs_do_not_expose_fallback_provisioning() -> None:
    public_docs = [
        ROOT / "README.md",
        ROOT / "INSTALL.md",
        ROOT / "PLUGIN.md",
        ROOT / "plugins/simplicio/README.md",
        ROOT / "plugins/simplicio-hermes/README.md",
    ]

    for path in public_docs:
        text = path.read_text(encoding="utf-8").lower()
        assert "pip install --upgrade simplicio-mapper" not in text
        assert "simplicio_mapper" not in text
        assert "simplicio_mapper_bin" not in text
        assert "simplicio_mapper_root" not in text


SURFACES = {
    "native-plugin", "agent-plugin-v1", "native-extension", "runtime-mcp",
    "guided-runtime", "delegated-cli",
}

# The twelve harnesses of the Runtime bot study: id -> (name, surface, preHooks).
# The Runtime writes a file for the first four (`runtime-mcp`, as for every other
# host it registers); for the other eight it writes nothing, so they take the
# categories the registry already has for a host the installer does not write:
# `guided-runtime` for the URL bots and the cloud bots, `delegated-cli` for the
# harness that runs other agents. The Runtime installs no pre-hook for those
# eight, so whatever the product has is host-managed.
BOT_STUDY_ROWS = {
    "grok": ("xAI Grok Build", "runtime-mcp", "runtime-managed"),
    "muse-code": ("Meta Muse Code", "runtime-mcp", "runtime-managed"),
    "openmausbot": ("OpenMausBot", "runtime-mcp", "runtime-managed"),
    "openmuse": ("OpenMuse (Python)", "runtime-mcp", "runtime-managed"),
    "t3-code": ("T3 Code", "delegated-cli", "host-managed"),
    "opendots": ("CopilotKit OpenDots", "guided-runtime", "host-managed"),
    "openbot": ("CopilotKit OpenBot", "guided-runtime", "host-managed"),
    "agentes-chat": ("agentes.chat", "guided-runtime", "host-managed"),
    "dots": ("OpenAI dots", "guided-runtime", "host-managed"),
    "grok-bot": ("xAI Grok Bot", "guided-runtime", "host-managed"),
    "muse": ("Meta Muse app", "guided-runtime", "host-managed"),
    "cue": ("Cue by Manus", "guided-runtime", "host-managed"),
}


def test_host_surface_registry_is_complete_and_honest() -> None:
    registry = _load_json("plugins/simplicio/host-surfaces.json")
    hosts = registry["hosts"]
    ids = {host["id"] for host in hosts}

    assert len(hosts) == len(ids) == 43
    assert {"claude-code", "codex", "cursor", "github-copilot", "kiro",
            "qwen-code", "gemini", "opencode", "pi", "orca-dev"} <= ids
    assert set(BOT_STUDY_ROWS) <= ids
    for host in hosts:
        assert host["preHooks"] in {"runtime-managed", "host-managed"}
        assert host["surface"] in SURFACES
        if "manifest" in host:
            assert (ROOT / "plugins/simplicio" / host["manifest"]).is_file()


def test_bot_study_hosts_have_the_surface_of_their_kind() -> None:
    hosts = {host["id"]: host for host in _load_json("plugins/simplicio/host-surfaces.json")["hosts"]}
    for host_id, (name, surface, pre_hooks) in BOT_STUDY_ROWS.items():
        row = hosts[host_id]
        assert (row["name"], row["surface"], row["preHooks"]) == (name, surface, pre_hooks), host_id
        # Nothing is bundled for these hosts: the Runtime writes their file or prints a route.
        assert "manifest" not in row, host_id
    # `grok` is xAI Grok Build; an earlier row described another product.
    assert "superagent" not in json.dumps(hosts["grok"]).lower()


def test_published_adapters_point_to_their_canonical_commands() -> None:
    prompt = _load_json("plugins/simplicio-prompt/.claude-plugin/plugin.json")
    assert prompt["name"] == "simplicio-prompt"
    assert (ROOT / "plugins/simplicio-prompt/commands/simplicio.md").is_file()
    assert (ROOT / "plugins/simplicio-prompt/hooks/plugin-runtime-adapter/adapter.mjs").is_file()


def test_local_publisher_includes_gemini_and_rejects_version_drift(tmp_path, monkeypatch) -> None:
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_manifest_parity", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    expected = {
        "plugins/simplicio/plugin.json",
        "plugins/simplicio/.codex-plugin/plugin.json",
        "plugins/simplicio/.claude-plugin/plugin.json",
        "plugins/simplicio/gemini-extension.json",
    }
    assert set(module.PLUGIN_MANIFESTS) == expected

    for relative in module.PLUGIN_MANIFESTS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        version = "0.2.10" if relative.endswith("gemini-extension.json") else "0.2.11"
        path.write_text(json.dumps({"name": "simplicio", "version": version}), encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    with pytest.raises(module.PublishError, match="plugin manifest versions differ"):
        module.plugin_manifests()


def test_loop_bundle_uses_canonical_reference_paths() -> None:
    loop_root = ROOT / "plugin/skills/simplicio-loop"
    tasks_root = ROOT / "plugin/skills/simplicio-tasks"

    assert not (tasks_root / "references").exists()
    assert (loop_root / "references/LLM_MAX_SPEED_ORIENTATION.md").is_file()

    loop_skill = (loop_root / "SKILL.md").read_text(encoding="utf-8")
    tasks_skill = (tasks_root / "SKILL.md").read_text(encoding="utf-8")
    orient_skill = (ROOT / "plugin/skills/simplicio-orient/SKILL.md").read_text(encoding="utf-8")
    assert "references/LLM_MAX_SPEED_ORIENTATION.md" in loop_skill
    assert "../simplicio-loop/references/LLM_MAX_SPEED_ORIENTATION.md" in orient_skill
    assert "../simplicio-loop/references/extension-points.md" in tasks_skill
    assert ".claude/skills/simplicio-loop/SKILL.md" not in tasks_skill
    assert "simplicio-global-llm-architecture-rules:start" not in tasks_skill

    for relative in ("plugin/scripts/web_verify.py", "plugin/scripts/video_evidence.py"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "plugin/skills/simplicio-loop/references/" in source
