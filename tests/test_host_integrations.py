from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1] / "pypi" / "simplicio"
sys.path.insert(0, str(PACKAGE_ROOT))

from simplicio.host_integrations import (
    COMPATIBILITY_MATRIX_HOST_IDS,
    HOSTS,
    INSTALLER_HOSTS,
    build_summary,
    compatibility_matrix,
    detect_hosts,
    write_summary,
)


BOT_STUDY_WRITTEN = frozenset({"grok", "muse-code", "openmausbot", "openmuse"})
BOT_STUDY_ROUTE_ONLY = frozenset(
    {"t3-code", "opendots", "openbot", "agentes-chat", "dots", "grok-bot", "muse", "cue"}
)


def _command(path: Path) -> None:
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def test_matrix_has_unique_ids_and_all_parent_children() -> None:
    ids = [spec.host_id for spec in HOSTS]
    assert len(ids) == len(set(ids))
    assert all(spec.minimum_version for spec in HOSTS)
    for expected in {
        "claude-code",
        "cursor",
        "deepseek-harness",
        "opencode",
        "vscode",
        "antigravity",
        "kiro",
        "pi",
        "oh-my-pi",
        "orca",
        "command-code",
    }:
        assert expected in ids


def test_detection_uses_exact_executable_and_app_evidence(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "claude")
    home = tmp_path / "home"
    (home / ".cursor").mkdir(parents=True)
    (home / ".cursor" / "mcp.json").write_text("{}", encoding="utf-8")
    snapshot = detect_hosts(home=home, env={"PATH": str(bin_dir)})
    by_id = {item["id"]: item for item in snapshot}
    assert by_id["claude-code"]["status"] == "detected"
    assert by_id["claude-code"]["executable"].endswith("/claude")
    assert by_id["cursor"]["status"] == "detected"
    assert by_id["deepseek-harness"]["status"] == "unsupported"


def test_claude_code_has_runtime_verification_contract() -> None:
    claude = next(spec for spec in HOSTS if spec.host_id == "claude-code")
    assert claude.executable_names == ("claude",)
    assert claude.config_paths == ("~/.claude/settings.json", "~/.claude/.mcp.json")
    assert claude.capability == "runtime-mcp"
    assert claude.verification_command[-1] == "--json"
    assert "<absolute-path>" in claude.verification_command
    assert claude.mcp_environment == (
        ("SIMPLICIO_RUNTIME_MODE", "mapper-only"),
        ("SIMPLICIO_MCP_PROFILE", "mapper-only"),
    )


def test_cursor_declares_user_and_workspace_scopes() -> None:
    cursor = next(spec for spec in HOSTS if spec.host_id == "cursor")
    assert cursor.executable_names == ("cursor",)
    assert cursor.scopes == ("user", "workspace")
    assert cursor.default_scope == "user"
    assert cursor.config_paths == ("~/.cursor/mcp.json", ".cursor/mcp.json")


def test_deepseek_harness_is_fail_closed_until_contract_is_verified() -> None:
    deepseek = next(spec for spec in HOSTS if spec.host_id == "deepseek-harness")
    assert deepseek.executable_names == ()
    assert deepseek.capability == "unsupported"
    assert deepseek.contract == "unverified"
    assert deepseek.verification_command == ()


def test_opencode_is_native_plugin_with_full_mode() -> None:
    opencode = next(spec for spec in HOSTS if spec.host_id == "opencode")
    assert opencode.executable_names == ("opencode",)
    assert opencode.config_paths == ("~/.config/opencode/opencode.json", "opencode.json")
    assert opencode.capability == "native-plugin"
    assert opencode.verification_command[:3] == ("simplicio", "mcp", "register")
    assert opencode.default_scope == "user"
    assert opencode.mcp_environment == (
        ("SIMPLICIO_RUNTIME_MODE", "full"),
        ("SIMPLICIO_MCP_PROFILE", "full"),
    )


def test_vscode_declares_all_supported_configuration_scopes() -> None:
    vscode = next(spec for spec in HOSTS if spec.host_id == "vscode")
    assert vscode.executable_names == ("code", "code-insiders")
    assert vscode.scopes == ("user", "workspace", "remote")
    assert vscode.default_scope == "user"
    assert vscode.config_paths == ("~/.vscode/mcp.json", ".vscode/mcp.json")
    assert vscode.verification_command[-1] == "--json"


def test_antigravity_uses_runtime_registration() -> None:
    spec = next(spec for spec in HOSTS if spec.host_id == "antigravity")
    assert spec.capability == "runtime-mcp"
    assert spec.config_paths == ("~/.gemini/config/mcp_config.json",)


def test_kiro_has_runtime_registration_contract() -> None:
    kiro = next(spec for spec in HOSTS if spec.host_id == "kiro")
    assert kiro.executable_names == ("kiro-cli",)
    assert kiro.config_paths == ("~/.kiro/settings/mcp.json", ".kiro/settings/mcp.json")
    assert kiro.capability == "runtime-mcp"
    assert kiro.verification_command[:3] == ("simplicio", "mcp", "register")


def test_pi_and_oh_my_pi_use_separate_exact_host_entries() -> None:
    pi = next(spec for spec in HOSTS if spec.host_id == "pi")
    omp = next(spec for spec in HOSTS if spec.host_id == "oh-my-pi")
    assert pi.executable_names == ("pi",)
    assert omp.executable_names == ("omp",)
    assert pi.host_id != omp.host_id
    assert pi.capability == omp.capability == "runtime-mcp"
    assert pi.verification_command == omp.verification_command


def test_orca_uses_portable_cli_verification_without_worktree_mutation() -> None:
    orca = next(spec for spec in HOSTS if spec.host_id == "orca")
    assert orca.executable_names == ("orca",)
    assert orca.capability == "portable-cli"
    assert orca.contract == "documented-cli"
    assert orca.verification_command == ("orca", "status", "--json")
    assert "worktrees" in orca.reason


def test_compatibility_matrix_covers_every_requested_remaining_host() -> None:
    by_id = {spec.host_id: spec for spec in HOSTS}
    assert COMPATIBILITY_MATRIX_HOST_IDS <= set(by_id)
    assert len(COMPATIBILITY_MATRIX_HOST_IDS) == 33
    assert BOT_STUDY_WRITTEN | BOT_STUDY_ROUTE_ONLY <= COMPATIBILITY_MATRIX_HOST_IDS
    for host_id in COMPATIBILITY_MATRIX_HOST_IDS - {spec.host_id for spec in INSTALLER_HOSTS}:
        spec = by_id[host_id]
        assert spec.contract == "unverified"
        assert spec.capability == "unsupported"
        assert spec.executable_names == ()


def test_compatibility_matrix_is_complete_and_redacted() -> None:
    matrix = compatibility_matrix()
    assert len(matrix) == len(HOSTS)
    assert {row["id"] for row in matrix} == {spec.host_id for spec in HOSTS}
    for row in matrix:
        assert set(row) == {
            "id", "name", "capability", "contract", "executable_names",
            "scopes", "verification", "documentation",
        }
        assert "token" not in json.dumps(row).lower()
        if row["contract"] == "unverified":
            assert row["capability"] == "unsupported"
            assert row["executable_names"] == []


def test_command_code_has_official_runtime_contract() -> None:
    command_code = next(spec for spec in HOSTS if spec.host_id == "command-code")
    assert command_code.executable_names == ("commandcode",)
    assert command_code.capability == "runtime-mcp"
    assert command_code.config_paths == ("~/.commandcode/mcp.json",)


def test_skip_controls_are_explicit_and_do_not_touch_host_files(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "cursor")
    home = tmp_path / "home"
    snapshot = detect_hosts(
        home=home,
        env={"PATH": str(bin_dir), "SIMPLICIO_SKIP_CURSOR": "1"},
    )
    cursor = next(item for item in snapshot if item["id"] == "cursor")
    assert cursor["status"] == "skipped"
    assert not home.exists()


def test_summary_reconciles_runtime_receipt_without_claiming_unknown_hosts(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "claude")
    summary = build_summary(
        runtime_report={"status": "passed", "registered": ["claude-code"]},
        home=tmp_path / "home",
        env={"PATH": str(bin_dir)},
    )
    by_id = {item["id"]: item for item in summary["hosts"]}
    assert by_id["claude-code"]["status"] == "registered"
    assert by_id["deepseek-harness"]["status"] == "unsupported"
    assert summary["runtime_registration"] == {"status": "passed"}


def test_summary_is_atomic_and_restrictive(tmp_path: Path) -> None:
    target = tmp_path / "state" / "host-integrations.json"
    write_summary(target, {"schema": "test", "hosts": []})
    assert json.loads(target.read_text(encoding="utf-8"))["schema"] == "test"
    assert os.stat(target).st_mode & 0o777 == 0o600
    assert not list(target.parent.glob("host-integrations.json.*"))

def test_native_write_receipts_and_dry_run(tmp_path):
    report = {"status": "passed", "dry_run": False, "writes": [
        {"label": "amp", "status": "done"},
        {"label": "kimi", "status": "skipped"},
        {"label": "droid", "status": "failed"},
    ], "skipped": ["qwen-code: malformed_json_preserved"]}
    hosts = {h["id"]: h for h in build_summary(report, home=tmp_path, env={"PATH": ""})["hosts"]}
    assert hosts["amp"]["status"] == "registered"
    assert hosts["kimi"]["status"] == "registered"
    assert hosts["droid"]["status"] == "failed"
    assert hosts["qwen-code"]["status"] == "skipped"
    report["dry_run"] = True
    dry = build_summary(report, home=tmp_path, env={"PATH": ""})
    assert not any(h["status"] == "registered" for h in dry["hosts"])


def test_windows_executable_suffix_is_recognized(tmp_path, monkeypatch):
    monkeypatch.setattr("simplicio.host_integrations.shutil.which", lambda name, path=None: str(tmp_path / (name + ".exe")))
    hosts = detect_hosts(home=tmp_path, env={"PATH": ""})
    assert next(h for h in hosts if h["id"] == "codex")["status"] == "detected"


def test_bot_study_hosts_the_runtime_writes_are_runtime_mcp_rows() -> None:
    by_id = {spec.host_id: spec for spec in HOSTS}
    installer = {spec.host_id for spec in INSTALLER_HOSTS}
    expected = {
        "grok": ("grok", "~/.grok/config.toml"),
        "muse-code": ("muse", "~/.config/muse/settings.json"),
        "openmausbot": ("openmausbot", "~/.openmausbot/config.json"),
        "openmuse": ("openmuse", "~/.openmuse/config.toml"),
    }
    assert set(expected) == BOT_STUDY_WRITTEN
    assert BOT_STUDY_WRITTEN <= installer
    for host_id, (executable, config) in expected.items():
        spec = by_id[host_id]
        assert spec.executable_names == (executable,), host_id
        assert spec.config_paths == (config,), host_id
        assert spec.capability == "runtime-mcp", host_id
        assert spec.contract == "delegated-to-runtime", host_id
        assert spec.verification_command[:3] == ("simplicio", "mcp", "register"), host_id
        assert spec.documentation.startswith("https://"), host_id
        # Written from documentation or from reading the package: nothing was run.
        assert "not verified against a real" in spec.reason.lower(), host_id
    # The id `grok` is xAI Grok Build, not the Superagent CLI an earlier row named.
    grok = by_id["grok"]
    assert "Grok Build" in grok.name
    assert "superagent" not in (grok.name + grok.documentation + grok.reason).lower()
    assert "settings.json" not in " ".join(grok.config_paths)


def test_bot_study_hosts_without_a_file_are_unverified_and_never_probed() -> None:
    by_id = {spec.host_id: spec for spec in HOSTS}
    installer = {spec.host_id for spec in INSTALLER_HOSTS}
    assert not BOT_STUDY_ROUTE_ONLY & installer
    for host_id in BOT_STUDY_ROUTE_ONLY:
        spec = by_id[host_id]
        assert spec.contract == "unverified", host_id
        assert spec.capability == "unsupported", host_id
        assert spec.executable_names == () and spec.config_paths == (), host_id
        assert spec.verification_command == (), host_id
        assert spec.documentation.startswith("https://"), host_id
        assert "not verified against a real installation" in spec.reason.lower(), host_id
        assert "writes nothing" in spec.reason, host_id
        # The reason names the command that tells the user what to do.
        command = (
            "simplicio integrate verify --host t3-code"
            if host_id == "t3-code"
            else f"simplicio integrations routes {host_id}"
        )
        assert command in spec.reason, host_id


def test_bot_study_hosts_are_detected_or_reported_without_a_guess(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # Commands of the four hosts the Runtime writes for, and names a guess could take.
    for name in ("grok", "muse", "openmausbot", "openmuse", "t3", "t3code", "dots", "cue", "openbot"):
        _command(bin_dir / name)
    snapshot = {
        item["id"]: item
        for item in detect_hosts(home=tmp_path / "home", env={"PATH": str(bin_dir)})
    }
    for host_id in BOT_STUDY_WRITTEN:
        assert snapshot[host_id]["status"] == "detected", host_id
        assert snapshot[host_id]["executable"], host_id
    for host_id in BOT_STUDY_ROUTE_ONLY:
        assert snapshot[host_id]["status"] == "unsupported", host_id
        assert snapshot[host_id]["executable"] is None, host_id
    assert not (tmp_path / "home").exists()


def test_bot_study_hosts_are_in_the_compatibility_matrix_with_their_contract() -> None:
    rows = {row["id"]: row for row in compatibility_matrix()}
    for host_id in BOT_STUDY_WRITTEN:
        assert rows[host_id]["capability"] == "runtime-mcp", host_id
        assert rows[host_id]["contract"] == "delegated-to-runtime", host_id
    for host_id in BOT_STUDY_ROUTE_ONLY:
        assert rows[host_id]["capability"] == "unsupported", host_id
        assert rows[host_id]["contract"] == "unverified", host_id
        assert rows[host_id]["executable_names"] == [], host_id
