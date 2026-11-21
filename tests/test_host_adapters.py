from __future__ import annotations

import json
from pathlib import Path

from simplicio.host_adapters import install_detected_hosts, portable_cli_plan
from simplicio.host_integrations import HOSTS, HostSpec


def _command(path: Path) -> None:
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def _spec(host_id: str = "fixture") -> HostSpec:
    return HostSpec(
        host_id=host_id,
        name="Fixture Host",
        executable_names=(host_id,),
        config_paths=("~/.fixture/config.json",),
        capability="runtime-mcp",
        contract="delegated-to-runtime",
        scopes=("user",),
    )


def test_multi_host_install_preserves_unrelated_json_and_is_idempotent(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "fixture")
    home = tmp_path / "home"
    config = home / ".fixture" / "config.json"
    config.parent.mkdir(parents=True)
    original = {"theme": "dark", "servers": {"other": {"command": "other"}}}
    config.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")

    first = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir)},
        specs=(_spec(),),
    )
    assert first["failed_hosts"] == []
    assert first["counts"]["registered"] == 1
    assert json.loads(config.read_text(encoding="utf-8"))["theme"] == "dark"
    assert config.with_name("config.json.simplicio.bak").is_file()

    second = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir)},
        specs=(_spec(),),
    )
    assert second["failed_hosts"] == []
    assert second["results"][0]["reason_code"] == "already_registered"


def test_dry_run_and_skip_do_not_mutate_files(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "fixture")
    home = tmp_path / "home"
    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir), "SIMPLICIO_SKIP_FIXTURE": "1"},
        dry_run=True,
        specs=(_spec(),),
    )
    assert result["counts"] == {"skipped": 1}
    assert not home.exists()


def test_malformed_config_isolated_as_failure(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "fixture")
    home = tmp_path / "home"
    config = home / ".fixture" / "config.json"
    config.parent.mkdir(parents=True)
    config.write_text("not json", encoding="utf-8")
    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir)},
        specs=(_spec(),),
    )
    assert result["failed_hosts"] == ["fixture"]
    assert config.read_text(encoding="utf-8") == "not json"


def test_claude_code_contract_uses_exact_probe_and_user_scope(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "claude-code")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "claude")
    home = tmp_path / "home"
    config = home / ".claude" / "settings.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"model": "sonnet"}) + "\n", encoding="utf-8")

    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir)},
        specs=(spec,),
    )

    assert result["failed_hosts"] == []
    assert result["results"][0]["status"] == "registered"
    document = json.loads(config.read_text(encoding="utf-8"))
    assert document["mcpServers"]["simplicio"]["command"] == "/opt/simplicio/bin/simplicio"
    assert document["mcpServers"]["simplicio"]["env"] == {
        "SIMPLICIO_RUNTIME_MODE": "mapper-only",
    }
    assert not (home / ".claude" / "settings.json.simplicio.bak").is_symlink()


def test_cursor_contract_selects_requested_user_or_workspace_scope(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "cursor")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "cursor")
    home = tmp_path / "home"
    workspace = tmp_path / "workspace"
    (home / ".cursor").mkdir(parents=True)
    (workspace / ".cursor").mkdir(parents=True)

    user = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=workspace,
        env={"PATH": str(bin_dir)}, scope="user", specs=(spec,)
    )
    workspace_result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=workspace,
        env={"PATH": str(bin_dir)}, scope="workspace", specs=(spec,)
    )

    assert user["failed_hosts"] == []
    assert workspace_result["failed_hosts"] == []
    assert json.loads((home / ".cursor/mcp.json").read_text())["mcpServers"]["simplicio"]
    assert json.loads((workspace / ".cursor/mcp.json").read_text())["mcpServers"]["simplicio"]


def test_unverified_deepseek_harness_fails_closed_without_mutation(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "deepseek-harness")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "deepseek")
    home = tmp_path / "home"
    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio",
        home=home,
        cwd=tmp_path,
        env={"PATH": str(bin_dir)},
        specs=(spec,),
    )

    assert result["failed_hosts"] == []
    assert result["results"] == [{
        "host_id": "deepseek-harness",
        "status": "unsupported",
        "scope": "user",
        "config": None,
        "capability": "unsupported",
        "verification": "none",
        "reason_code": "unsupported",
        "changed": False,
        "backup": None,
    }]
    assert not home.exists()


def test_opencode_contract_registers_documented_user_config(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "opencode")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "opencode")
    home = tmp_path / "home"
    config = home / ".config/opencode/opencode.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"provider": "local"}) + "\n", encoding="utf-8")

    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(spec,)
    )

    assert result["failed_hosts"] == []
    document = json.loads(config.read_text(encoding="utf-8"))
    assert document["provider"] == "local"
    assert document["mcpServers"]["simplicio"]["args"] == ["serve", "--mcp", "--stdio"]
    assert document["mcpServers"]["simplicio"]["env"] == {"SIMPLICIO_RUNTIME_MODE": "full"}


def test_vscode_contract_supports_user_workspace_and_remote_scopes(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "vscode")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "code")
    home = tmp_path / "home"
    workspace = tmp_path / "remote-workspace"
    (home / ".vscode").mkdir(parents=True)
    (workspace / ".vscode").mkdir(parents=True)

    for scope in ("user", "workspace", "remote"):
        result = install_detected_hosts(
            "/opt/simplicio/bin/simplicio", home=home, cwd=workspace,
            env={"PATH": str(bin_dir)}, scope=scope, specs=(spec,)
        )
        assert result["failed_hosts"] == []

    assert json.loads((home / ".vscode/mcp.json").read_text())["mcpServers"]["simplicio"]
    assert json.loads((workspace / ".vscode/mcp.json").read_text())["mcpServers"]["simplicio"]


def test_unverified_antigravity_is_reported_without_guessing_a_binary(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "antigravity")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "antigravity")
    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=tmp_path / "home", cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(spec,)
    )

    assert result["results"][0]["status"] == "absent"
    assert result["results"][0]["reason_code"] == "absent"


def test_kiro_contract_is_atomic_and_idempotent(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "kiro")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "kiro-cli")
    home = tmp_path / "home"
    config = home / ".kiro/settings/mcp.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"enabled": True}) + "\n", encoding="utf-8")

    first = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(spec,)
    )
    second = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(spec,)
    )

    assert first["failed_hosts"] == []
    assert second["results"][0]["reason_code"] == "already_registered"
    assert json.loads(config.read_text())["enabled"] is True


def test_pi_and_oh_my_pi_use_separate_exact_executables_and_configs(tmp_path: Path) -> None:
    pi = next(item for item in HOSTS if item.host_id == "pi")
    omp = next(item for item in HOSTS if item.host_id == "oh-my-pi")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "pi")
    _command(bin_dir / "omp")
    home = tmp_path / "home"

    pi_result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(pi,)
    )
    omp_result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(omp,)
    )

    assert pi_result["failed_hosts"] == []
    assert omp_result["failed_hosts"] == []
    assert pi_result["results"][0]["status"] == "requires-runtime-registration"
    assert omp_result["results"][0]["status"] == "requires-runtime-registration"
    assert not home.exists()  # No invented generic MCP files for these hosts.


def test_orca_portable_contract_is_verification_only() -> None:
    spec = next(item for item in HOSTS if item.host_id == "orca")
    plan = portable_cli_plan(spec, "/usr/local/bin/orca")
    assert plan == {
        "host_id": "orca",
        "argv": ["/usr/local/bin/orca", "status", "--json"],
        "verification_only": True,
        "mutates_worktree": False,
        "reads_credentials": False,
    }


def test_command_code_contract_requires_an_official_contract(tmp_path: Path) -> None:
    spec = next(item for item in HOSTS if item.host_id == "command-code")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _command(bin_dir / "commandcode")
    home = tmp_path / "home"
    result = install_detected_hosts(
        "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
        env={"PATH": str(bin_dir)}, specs=(spec,)
    )
    assert result["results"][0]["status"] == "requires-runtime-registration"
    assert result["results"][0]["reason_code"] == "run_simplicio_mcp_register"
    assert not home.exists()


def test_generic_writer_never_writes_a_file_for_a_bot_study_host(tmp_path: Path) -> None:
    # The Runtime writes the files of these hosts (their formats are not the generic
    # JSON one: a marked TOML table, a strict schema, a schema_version); for the other
    # eight it writes nothing. Whatever is on PATH or on disk, this module writes nothing.
    written = ("grok", "muse-code", "openmausbot", "openmuse")
    route_only = ("t3-code", "opendots", "openbot", "agentes-chat", "dots", "grok-bot", "muse", "cue")
    specs = tuple(item for item in HOSTS if item.host_id in written + route_only)
    assert len(specs) == 12
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("grok", "muse", "openmausbot", "openmuse", "t3", "dots", "cue", "openbot"):
        _command(bin_dir / name)
    home = tmp_path / "home"
    existing = {
        ".grok/config.toml": "model = 'x'\n",
        ".config/muse/settings.json": "not json",
        ".openmausbot/config.json": "{}\n",
        ".openmuse/config.toml": "[llm]\n",
    }
    for relative, text in existing.items():
        target = home / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    before = sorted(str(path.relative_to(home)) for path in home.rglob("*"))

    for dry_run in (True, False):
        result = install_detected_hosts(
            "/opt/simplicio/bin/simplicio", home=home, cwd=tmp_path,
            env={"PATH": str(bin_dir)}, specs=specs, dry_run=dry_run,
        )
        by_id = {item["host_id"]: item for item in result["results"]}
        assert result["failed_hosts"] == []
        for host_id in written:
            assert by_id[host_id]["status"] == "requires-runtime-registration", host_id
            assert by_id[host_id]["reason_code"] == "run_simplicio_mcp_register", host_id
        for host_id in route_only:
            assert by_id[host_id]["status"] == "unsupported", host_id
            assert by_id[host_id]["config"] is None, host_id

    assert sorted(str(path.relative_to(home)) for path in home.rglob("*")) == before
    for relative, text in existing.items():
        assert (home / relative).read_text(encoding="utf-8") == text
