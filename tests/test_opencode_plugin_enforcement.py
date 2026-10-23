"""Enforcement and installer contract for the managed OpenCode plugin (#450).

These tests exercise the real host path instead of inspecting JSON:

* the installer repairs a legacy npm reference, installs the managed plugin
  directory and keeps third-party plugins, MCP servers and settings intact;
* ``verify`` returns a machine-readable verdict and a meaningful exit code;
* the host harness loads the plugin the way OpenCode V2 does and proves native
  ``read``/``write``/``edit``/``shell`` are rejected while ``simplicio_*`` and
  third-party tools pass;
* the "create an HTML file" scenario creates the file only through
  ``simplicio_edit`` and returns an ``simplicio.effect-receipt/v1`` write_set;
* the installed ``opencode`` binary loads the managed directory without the
  ``failed to load plugin`` warning.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "opencode_plugin.py"
PACKAGE = ROOT / "plugins" / "simplicio" / "opencode"
HARNESS = ROOT / "tests" / "node" / "opencode_host_harness.mjs"
CONFIG = Path(".config/opencode/opencode.json")

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is required for the host harness")


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("opencode_plugin_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime_binary() -> str | None:
    candidates = [os.environ.get("SIMPLICIO_BIN"), str(Path.home() / ".simplicio/bin/simplicio")]
    found = shutil.which("simplicio")
    if found:
        candidates.append(found)
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def base_config() -> dict:
    return {
        "$schema": "https://opencode.ai/config.json",
        "mcp": {
            "simplicio": {
                "type": "local",
                "command": ["/opt/simplicio/bin/simplicio", "serve", "--mcp", "--stdio", "--no-facade-mode"],
                "enabled": True,
                "environment": {"SIMPLICIO_MCP_PROFILE": "full", "SIMPLICIO_RUNTIME_MODE": "full"},
            },
            "github": {"type": "remote", "url": "https://api.githubcopilot.com/mcp/"},
        },
        "plugin": ["opencode-simplicio", "third-party-plugin"],
        "plugins": [
            {"package": "./plugins/local", "options": {"strict": True}},
            "https://example.test/third-party-plugin.git",
        ],
        "theme": "dark",
    }


def materialize(tmp_path: Path) -> tuple[Path, Path]:
    home = tmp_path / "home"
    config = home / CONFIG
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps(base_config(), indent=2) + "\n", encoding="utf-8")
    return home, config


def test_install_repairs_legacy_reference_and_preserves_third_parties(tmp_path: Path) -> None:
    home, config = materialize(tmp_path)
    module = load_module()

    receipt = module.install(home=home, config_path=config)

    assert receipt["ok"] is True, receipt["reasons"]
    assert receipt["changed"] is True
    assert receipt["removed"] == ["opencode-simplicio"]
    assert set(receipt["verification"]["plugin"]["hook"]["blocked"]) == {"read", "write", "edit", "shell"}
    assert receipt["verification"]["plugin"]["hook"]["verified"] == "dynamic"
    assert receipt["verification"]["plugin"]["hook"]["leaked"] == []

    document = json.loads(config.read_text(encoding="utf-8"))
    managed = str((home / ".simplicio/hooks/opencode-simplicio").resolve())
    assert document["plugins"][-1] == managed
    assert {"package": "./plugins/local", "options": {"strict": True}} in document["plugins"]
    assert "https://example.test/third-party-plugin.git" in document["plugins"]
    assert document["plugin"] == ["third-party-plugin"]
    assert "opencode-simplicio" not in document["plugins"]
    assert document["mcp"]["github"] == base_config()["mcp"]["github"]
    assert document["mcp"]["simplicio"]["environment"]["SIMPLICIO_MCP_PROFILE"] == "full"
    assert document["theme"] == "dark"
    assert (home / ".simplicio/hooks/opencode-simplicio/index.js").is_file()
    assert (home / ".simplicio/hooks/opencode-simplicio/package.json").is_file()
    assert receipt["backup"] and Path(receipt["backup"]).is_file()

    again = module.install(home=home, config_path=config)
    assert again["ok"] is True
    assert again["changed"] is False
    assert again["removed"] == []


def test_verify_reports_resolved_plugin_and_active_hook(tmp_path: Path, capsys) -> None:
    home, config = materialize(tmp_path)
    module = load_module()
    module.install(home=home, config_path=config)

    report = module.verify(home=home, config_path=config)

    assert report["schema"] == "simplicio.opencode-verify/v1"
    assert report["ok"] is True, report["reasons"]
    assert report["plugin"]["resolved"] is True
    assert report["plugin"]["api"] == "opencode-v2"
    hook = report["plugin"]["hook"]
    assert hook["name"] == "execute.before"
    assert hook["registered"] is True
    assert hook["verified"] == "dynamic"
    assert report["mcp"]["present"] is True
    assert report["mcp"]["server_count"] == 2

    exit_code = module.main(["verify", "--home", str(home), "--config", str(config), "--json"])
    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert captured["ok"] is True


def test_verify_fails_when_the_enforcing_entrypoint_is_missing(tmp_path: Path, capsys) -> None:
    home, config = materialize(tmp_path)
    module = load_module()
    module.install(home=home, config_path=config)
    (home / ".simplicio/hooks/opencode-simplicio/index.js").unlink()

    exit_code = module.main(["verify", "--home", str(home), "--config", str(config), "--json"])
    report = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert report["ok"] is False
    assert "plugin_not_declared_or_missing" in report["reasons"]


def test_verify_fails_when_a_legacy_npm_reference_is_still_declared(tmp_path: Path) -> None:
    home, config = materialize(tmp_path)
    module = load_module()
    module.install(home=home, config_path=config)
    document = json.loads(config.read_text(encoding="utf-8"))
    document["plugins"].append("opencode-simplicio")
    config.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    report = module.verify(home=home, config_path=config)

    assert report["ok"] is False
    assert "legacy_npm_reference" in report["reasons"]
    assert any(reference == "opencode-simplicio" for reference in report["config"]["declared"])


def test_verify_fails_when_the_managed_mcp_entry_is_absent(tmp_path: Path) -> None:
    home, config = materialize(tmp_path)
    module = load_module()
    module.install(home=home, config_path=config)
    document = json.loads(config.read_text(encoding="utf-8"))
    document["mcp"].pop("simplicio")
    config.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    report = module.verify(home=home, config_path=config)

    assert report["ok"] is False
    assert "managed_mcp_entry_missing" in report["reasons"]


def run_harness(*arguments: str, timeout: int = 120) -> dict:
    completed = subprocess.run(
        ["node", str(HARNESS), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert lines, completed.stderr
    payload = json.loads(lines[-1])
    assert completed.returncode == (0 if payload.get("ok") else 1), (completed.returncode, payload, completed.stderr)
    return payload


def test_host_harness_blocks_native_tools_and_allows_third_parties() -> None:
    payload = run_harness("contract", "--plugin", str(PACKAGE), timeout=60)

    assert payload["ok"] is True
    assert payload["plugin"] == {
        "id": "simplicio",
        "entry": str(PACKAGE / "index.js"),
        "hook": "execute.before",
    }
    assert set(payload["blocked"]) == {"read", "write", "edit", "shell"}
    assert set(payload["v1_blocked"]) == {"read", "write", "edit", "shell"}
    for tool, message in payload["blocked"].items():
        assert "Simplicio is mandatory" in message
        assert "simplicio_" in message
    assert all(message is None for message in payload["passthrough"].values())


MCP_BINARY = runtime_binary()


@pytest.mark.skipif(MCP_BINARY is None, reason="installed Simplicio runtime is required for the MCP receipt")
def test_html_task_uses_governed_edit_and_returns_a_write_set_receipt(tmp_path: Path) -> None:
    payload = run_harness(
        "html",
        "--plugin",
        str(PACKAGE),
        "--repo",
        str(tmp_path),
        "--binary",
        str(MCP_BINARY),
    )

    assert payload["ok"] is True, payload
    acceptance = payload["acceptance"]
    assert acceptance["native_write_blocked"] is True
    assert acceptance["second_native_write_blocked"] is True
    assert acceptance["file_created_by_governed_edit"] is True
    assert acceptance["file_bytes"] > 0
    assert acceptance["receipt_schema"] == "simplicio.effect-receipt/v1"
    assert "index.html" in acceptance["write_set"]
    assert (tmp_path / "index.html").is_file()
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.skipif(
    shutil.which("opencode") is None or os.environ.get("SIMPLICIO_SKIP_OPENCODE_HOST") == "1",
    reason="installed OpenCode is required to prove the host loader accepts the managed directory",
)
def test_installed_opencode_loads_the_managed_directory_without_failures(tmp_path: Path) -> None:
    module = load_module()
    home = tmp_path / "home"
    config = home / CONFIG
    config.parent.mkdir(parents=True)
    config.write_text(
        json.dumps({"mcp": {"simplicio": base_config()["mcp"]["simplicio"]}, "plugins": []}, indent=2) + "\n",
        encoding="utf-8",
    )
    receipt = module.install(home=home, config_path=config)
    assert receipt["ok"] is True, receipt["reasons"]

    xdg = tmp_path / "xdg"
    config_home = xdg / "config" / "opencode"
    config_home.mkdir(parents=True)
    shutil.copy2(config, config_home / "opencode.json")
    for name in ("data", "cache", "state"):
        (xdg / name).mkdir(parents=True)
    environment = {
        **os.environ,
        "XDG_CONFIG_HOME": str(xdg / "config"),
        "XDG_DATA_HOME": str(xdg / "data"),
        "XDG_CACHE_HOME": str(xdg / "cache"),
        "XDG_STATE_HOME": str(xdg / "state"),
    }
    process = subprocess.Popen(
        [
            shutil.which("opencode"),
            "run",
            "--standalone",
            "--print-logs",
            "--log-level",
            "info",
            "--model",
            os.environ.get("SIMPLICIO_OPENCODE_MODEL", "opencode-go/beam-free"),
            "reply OK",
        ],
        cwd=xdg / "data",
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        output, _ = process.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        process.kill()
        output, _ = process.communicate()

    managed = str((home / ".simplicio/hooks/opencode-simplicio").resolve())
    assert managed in output, output[-4000:]
    assert "failed to load plugin" not in output, output[-4000:]
    assert "configured plugin path must be a directory" not in output, output[-4000:]
