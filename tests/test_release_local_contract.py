from __future__ import annotations

import json
import re
import importlib.util
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
INSTALLER = ROOT / "install.ps1"


def test_powershell_variables_followed_by_colon_are_braced():
    source = INSTALLER.read_text(encoding="utf-8")
    invalid = re.findall(
        r"\$(?!(?:env|global|script|local|private|using):)([A-Za-z_][A-Za-z0-9_]*):",
        source,
    )
    assert invalid == []
    assert "${LASTEXITCODE}: $detail" in source


def test_powershell_install_paths_use_windows_separators_and_join_path():
    source = INSTALLER.read_text(encoding="utf-8")
    assert '$InstallDir = Join-Path $env:USERPROFILE ".simplicio\\bin"' in source
    assert '$InstallDir = "$env:USERPROFILE\\.simplicio\\bin"' not in source
    assert "Join-Path $InstallDir" in source
    assert '$InstallDir = "$env:USERPROFILE/.simplicio/bin"' not in source


def test_mcp_docs_use_copy_safe_absolute_paths_for_every_platform():
    for relative in ("README.md", "MCP-CONNECT.md"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert 'command = "C:/Users/YourName/.simplicio/bin/simplicio.exe"' in source
        assert 'command = "/Users/your-name/.simplicio/bin/simplicio"' in source
        assert 'command = "/home/your-name/.simplicio/bin/simplicio"' in source
        assert 'command = "~/.simplicio/bin/simplicio"' not in source
        assert not re.search(r'command\s*=\s*"[A-Za-z]:\\(?!\\)', source)


def test_all_readmes_document_pypi_and_direct_installer_paths():
    readmes = [ROOT / "README.md", *sorted((ROOT / "READMEs").glob("README.*.md"))]
    assert len(readmes) == 15
    for path in readmes:
        source = path.read_text(encoding="utf-8")
        assert "simplicio-installer" in source, path
        assert "pip install" in source, path
        assert "install.sh" in source, path
        assert "install.ps1" in source, path


def test_powershell_parser_accepts_the_public_installer():
    pwsh = shutil.which("pwsh")
    assert pwsh is not None, "pwsh is a required local release-test dependency"
    path = str(INSTALLER).replace("'", "''")
    script = (
        f"$path='{path}'; $tokens=$null; $errors=$null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        "$path,[ref]$tokens,[ref]$errors) > $null; "
        "if ($errors.Count -ne 0) { "
        "$errors | ForEach-Object { Write-Error $_.Message }; exit 1 }"
    )
    result = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_public_repository_owns_local_pypi_and_release_publication():
    publisher = ROOT / "scripts/publish_release_local.py"
    assert publisher.is_file()
    source = publisher.read_text(encoding="utf-8")
    assert "pypi/simplicio" in source
    assert "twine" in source
    assert "simpletibr/simplicio" in source
    assert "workflow" not in source.lower()
    assert "simplicio-runtime" not in source


def test_public_publisher_uses_post_release_smoke_cli_contract():
    publisher = (ROOT / "scripts/publish_release_local.py").read_text(encoding="utf-8")
    assert '"--repo", PUBLIC_REPOSITORY' in publisher
    assert '"--repository"' not in publisher
    assert '"core.whitespace=cr-at-eol"' in publisher


def test_public_publisher_stages_versioned_codex_hooks(tmp_path, monkeypatch):
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_hooks", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    bundle = tmp_path / "bundle"
    public = tmp_path / "public"
    for relative in module.CODEX_HOOK_FILES:
        source = bundle / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("fixture " + relative + "\n", encoding="utf-8")
    (bundle / "codex/mcp-route.sh").chmod(0o755)

    monkeypatch.setattr(module, "ROOT", public)
    changed = module.stage_codex_hooks(bundle)

    assert {path.relative_to(public).as_posix() for path in changed} == set(
        module.CODEX_HOOK_FILES
    )
    for relative in module.CODEX_HOOK_FILES:
        assert (public / relative).read_bytes() == (bundle / relative).read_bytes()
    assert (public / "codex/mcp-route.sh").stat().st_mode & 0o111



def test_public_publisher_keeps_executables_out_of_the_source_commit(tmp_path, monkeypatch):
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_assets", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    bundle = tmp_path / "bundle"
    public = tmp_path / "public"
    bundle.mkdir()
    public.mkdir()
    for name in module.required_release_assets():
        (bundle / name).write_bytes(("fixture:" + name).encode("utf-8"))

    monkeypatch.setattr(module, "ROOT", public)
    changed = module.stage_bundle(bundle)
    changed_names = {path.relative_to(public).as_posix() for path in changed}

    assert changed_names == set(module.required_release_assets()) - set(module.ASSETS)
    assert not (changed_names & set(module.ASSETS))
    for name in module.required_release_assets():
        assert (public / name).read_bytes() == (bundle / name).read_bytes()


def test_publication_paths_gate_the_executable_codex_hook_contract():
    publisher = (ROOT / "scripts/publish_release_local.py").read_text(encoding="utf-8")
    assert 'shutil.which("pwsh")' in publisher
    assert 'str(ROOT / "tests/test_codex_hooks.sh")' in publisher
    assert 'timeout=300' in publisher
    assert publisher.count("verify_codex_hook_contract(bundle)") == 2


def test_publication_fails_closed_when_powershell_is_unavailable(monkeypatch):
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_pwsh", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.shutil, "which", lambda _name: None)

    try:
        module.verify_codex_hook_contract(ROOT / "dist" / "bundle")
    except module.PublishError as exc:
        assert "PowerShell is required" in str(exc)
    else:
        raise AssertionError("publication accepted a skipped Windows hook contract")


def test_public_publisher_requires_pr_merge_before_tagging():
    publisher = (ROOT / "scripts/publish_release_local.py").read_text(encoding="utf-8")
    assert '"gh", "pr", "create"' in publisher
    assert '"gh", "pr", "merge"' in publisher
    assert '["git", "push", "origin", "master"]' not in publisher
    assert '["git", "merge", "--ff-only", "origin/master"]' in publisher


def test_public_publisher_can_resume_after_an_external_partial_failure():
    source = (ROOT / "scripts/publish_release_local.py").read_text(encoding="utf-8")
    assert 'mode.add_argument("--resume"' in source
    assert "def resume_public_preflight(" in source
    assert "def resume_publish(" in source
    assert "already_published_to_pypi" in source



def test_publication_force_stages_only_known_installer_source_wrappers():
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_force_paths", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    for path in (
        "npm/simplicio/package.json",
        "npm/simplicio-installer/package.json",
        "npm/simplicio-unscoped/package.json",
        "pypi/simplicio/pyproject.toml",
        r"pypi\simplicio\simplicio\__main__.py",
    ):
        assert module.requires_forced_release_staging(path)

    for path in (
        "simplicio-macos-arm64",
        "simplicio-windows-x64.exe",
        "simplicio-macos-arm64.sig",
        "SHA256SUMS",
        "codex/mcp-route.sh",
        "scripts/publish_release_local.py",
    ):
        assert not module.requires_forced_release_staging(path)


def test_public_publisher_builds_wheel_from_clean_source(tmp_path, monkeypatch):
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local_clean_wheel", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    package = tmp_path / "package"
    source = package / "simplicio"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    cache = source / "__pycache__"
    cache.mkdir()
    (cache / "stale.pyc").write_bytes(b"stale")
    build = package / "build"
    build.mkdir()
    (build / "stale.txt").write_text("stale", encoding="utf-8")
    monkeypatch.setattr(module, "PACKAGE_ROOT", package)

    def fake_run(command, **_kwargs):
        if command[1:3] == ["-m", "build"]:
            clean_source = Path(command[-1])
            assert not (clean_source / "build").exists()
            assert not any(
                "__pycache__" in path.parts or path.suffix == ".pyc"
                for path in clean_source.rglob("*")
            )
            output = Path(command[command.index("--outdir") + 1])
            output.mkdir(parents=True, exist_ok=True)
            wheel = output / "simplicio_installer-3.8.31-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("simplicio/__init__.py", "")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(module, "run", fake_run)
    wheel = module.build_wheel(tmp_path / "output", "3.8.31")
    with zipfile.ZipFile(wheel) as archive:
        assert archive.namelist() == ["simplicio/__init__.py"]


PUBLIC_METADATA_WRAPPERS = (
    "npm/simplicio/package.json",
    "npm/simplicio-installer/package.json",
    "npm/simplicio-unscoped/package.json",
)
PUBLIC_METADATA_DESKTOP_FILES = (
    "apps/desktop/package.json", "apps/desktop/package-lock.json",
    "apps/desktop/src-tauri/tauri.conf.json", "apps/desktop/src-tauri/Cargo.toml",
    "apps/desktop/src-tauri/Cargo.lock",
)


def _load_publisher(name, tmp_path, monkeypatch):
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    return module


FLOW_SOURCE = "docs/flow/simplicio.flow.json"
FLOW_GENERATOR = "scripts/generate_flow.py"
FLOW_MERMAID = "docs/flow/simplicio.mmd"
FLOW_SVG = "docs/flow/simplicio.svg"
FLOW_LANGFLOW = "docs/flow/langflow/simplicio.langflow.json"


def _committed_flow_text():
    return (ROOT / FLOW_SOURCE).read_bytes().decode("utf-8")


def _committed_flow():
    return json.loads(_committed_flow_text())


def _flow_node_paths(document):
    """Every path a node of the flow names as its source or artifact."""
    paths = []
    for node in document["nodes"]:
        for key in ("source", "artifact"):
            value = node.get(key)
            if value and value not in paths:
                paths.append(value)
    return paths


def _copy_flow_tree(tmp_path):
    """The flow source, its generator, its generated files and what its nodes name.

    The generator derives its repository root from its own location and fails
    when a node names a path that is absent, so the fixture needs the real tree.
    """
    relatives = [
        FLOW_GENERATOR, FLOW_SOURCE, FLOW_MERMAID, FLOW_SVG, FLOW_LANGFLOW,
        *_flow_node_paths(_committed_flow()),
    ]
    for relative in relatives:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copyfile(source, target)


def _flow_tree(tmp_path):
    """Relative path -> bytes for every file under docs/flow of the fixture tree."""
    base = tmp_path / "docs/flow"
    return {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in sorted(base.rglob("*")) if path.is_file()
    }


def _relative_flow_paths(tmp_path, changed):
    return [
        path.relative_to(tmp_path).as_posix() for path in changed
        if path.relative_to(tmp_path).as_posix().startswith("docs/flow/")
    ]


def _write_public_metadata_tree(tmp_path):
    """Everything update_public_metadata reads, at version 3.8.30.

    The registry entry is a copy of the committed server.json, so a test can
    prove what the publisher does to the real file. The flow tree is a copy of
    the committed one and is written first, so that the fixture's own
    README.md, MCP-CONNECT.md and VERSION.md replace the copied node sources.
    """
    _copy_flow_tree(tmp_path)
    (tmp_path / "VERSION.md").write_text(
        "## Runtime snapshot: v3.8.30\n"
        "## Current Version: v3.8.30\n"
        "  `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`\n",
        encoding="utf-8",
    )
    for relative in ("README.md", "MCP-CONNECT.md"):
        (tmp_path / relative).write_text(
            "SIMPLICIO_CODEX_HOOK_REF=v3.8.30\n",
            encoding="utf-8",
        )
    for relative in PUBLIC_METADATA_WRAPPERS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        name = "@simpletibr/simplicio" if relative == PUBLIC_METADATA_WRAPPERS[0] else relative
        path.write_text(
            json.dumps(
                {"name": name, "version": "3.8.30", "description": "fixture"},
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    (tmp_path / "SIMPLICIO_ECOSYSTEM.md").write_text(
        "3.8.30 (release pública; quatro alvos)\n"
        "O manifest atualmente publicado neste repositório é o `3.8.30`.\n",
        encoding="utf-8",
    )
    for relative in PUBLIC_METADATA_DESKTOP_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, path)
    shutil.copyfile(ROOT / "server.json", tmp_path / "server.json")


def _update_public_metadata(module):
    return module.update_public_metadata(
        "v3.8.31",
        "3.8.31",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )


def test_public_publisher_updates_all_release_version_consumers(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_versions", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    wrappers = PUBLIC_METADATA_WRAPPERS
    desktop_files = PUBLIC_METADATA_DESKTOP_FILES

    changed = _update_public_metadata(module)
    assert (tmp_path / "version.txt").read_text(encoding="utf-8") == "3.8.31\n"
    assert all(json.loads((tmp_path / path).read_text())["version"] == "3.8.31" for path in wrappers)
    ecosystem = (tmp_path / "SIMPLICIO_ECOSYSTEM.md").read_text(encoding="utf-8")
    assert "3.8.30" not in ecosystem
    assert ecosystem.count("3.8.31") == 2
    assert tmp_path / "SIMPLICIO_ECOSYSTEM.md" in changed
    assert all(tmp_path / relative in changed for relative in desktop_files)
    for relative in desktop_files[:3]:
        assert json.loads((tmp_path / relative).read_text())["version"] == "3.8.31"
    assert json.loads((tmp_path / desktop_files[1]).read_text())["packages"][""]["version"] == "3.8.31"
    for relative in desktop_files[3:]:
        assert 'name = "simplicio-desktop"\nversion = "3.8.31"' in (tmp_path / relative).read_text()
    # The official MCP registry entry is a release version consumer too, and it
    # must be in the list the publisher stages for the release commit.
    assert tmp_path / "server.json" in changed
    server = json.loads((tmp_path / "server.json").read_text(encoding="utf-8"))
    assert server["version"] == "3.8.31"
    assert [package["version"] for package in server["packages"]] == ["3.8.31"]


def test_public_publisher_rewrites_only_the_registry_entry_versions(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_server_json", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    committed = (ROOT / "server.json").read_text(encoding="utf-8")
    current = json.loads(committed)["version"]

    _update_public_metadata(module)

    expected = committed.replace('"version": "%s"' % current, '"version": "3.8.31"')
    assert expected.count('"version": "3.8.31"') == 2
    assert (tmp_path / "server.json").read_bytes() == expected.encode("utf-8")


def test_public_publisher_rewrites_every_entry_of_the_scoped_wrapper_and_no_other(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_server_json_entries", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    scoped = server["packages"][0]
    other = {"registryType": "pypi", "identifier": "simplicio-installer", "version": "1.0.2",
             "transport": {"type": "stdio"}}
    mirror = dict(scoped, registryBaseUrl="https://registry.example.test", version="3.0.0")
    server["packages"] = [scoped, other, mirror]
    (tmp_path / "server.json").write_text(json.dumps(server, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _update_public_metadata(module)

    updated = json.loads((tmp_path / "server.json").read_text(encoding="utf-8"))
    assert updated["version"] == "3.8.31"
    assert [package["version"] for package in updated["packages"]] == ["3.8.31", "1.0.2", "3.8.31"]
    assert updated["packages"][1] == other


def _canonical(document):
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def _registry_entry():
    return json.loads((ROOT / "server.json").read_text(encoding="utf-8"))


def _entry_without_top_level_version():
    entry = _registry_entry()
    del entry["version"]
    return _canonical(entry)


def _entry_for_another_package():
    entry = _registry_entry()
    entry["packages"][0]["identifier"] = "@someone-else/simplicio"
    return _canonical(entry)


def _entry_without_packages():
    entry = _registry_entry()
    del entry["packages"]
    return _canonical(entry)


def _entry_with_empty_packages():
    entry = _registry_entry()
    entry["packages"] = []
    return _canonical(entry)


def _entry_with_non_object_package():
    entry = _registry_entry()
    entry["packages"] = ["@simpletibr/simplicio"]
    return _canonical(entry)


def _entry_that_is_not_an_object():
    return "[]\n"


def _entry_in_compact_form():
    return json.dumps(_registry_entry())


NO_ENTRY = "server.json has no package entry for @simpletibr/simplicio"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (None, "server.json is missing"),
        ("{not json", "server.json is not valid JSON"),
        (_entry_that_is_not_an_object(), "server.json has no top-level version"),
        (_entry_without_top_level_version(), "server.json has no top-level version"),
        (_entry_for_another_package(), NO_ENTRY),
        (_entry_without_packages(), NO_ENTRY),
        (_entry_with_empty_packages(), NO_ENTRY),
        (_entry_with_non_object_package(), NO_ENTRY),
        (_entry_in_compact_form(), "server.json must be two-space JSON"),
    ],
    ids=[
        "missing-file",
        "invalid-json",
        "not-an-object",
        "no-top-level-version",
        "no-package-for-the-wrapper",
        "no-packages-key",
        "empty-packages",
        "package-is-not-an-object",
        "not-in-the-canonical-two-space-form",
    ],
)
def test_public_publisher_fails_closed_on_a_registry_entry_it_cannot_rewrite(tmp_path, monkeypatch, body, message):
    module = _load_publisher("publish_release_local_server_json_closed", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    path = tmp_path / "server.json"
    if body is None:
        path.unlink()
    else:
        path.write_text(body, encoding="utf-8")

    with pytest.raises(module.PublishError, match=message):
        _update_public_metadata(module)

    # A refused rewrite must never leave a half-edited registry entry behind.
    assert (path.read_text(encoding="utf-8") if path.exists() else None) == body


@pytest.mark.parametrize(
    ("wrapper_body", "message"),
    [
        ('{\n  "version": "3.8.30",\n  "description": "fixture"\n}\n', "has no name"),
        ('{\n  "version": "3.8.30",\n  not json\n}\n', "is not valid JSON"),
    ],
    ids=["no-name", "invalid-json"],
)
def test_public_publisher_fails_closed_when_the_scoped_wrapper_cannot_name_the_registry_package(
    tmp_path, monkeypatch, wrapper_body, message
):
    module = _load_publisher("publish_release_local_server_json_wrapper", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    # The version line stays valid for the publisher's own wrapper rewrite, so
    # only the registry-entry step can notice the problem.
    (tmp_path / "npm/simplicio/package.json").write_text(wrapper_body, encoding="utf-8")
    before = (tmp_path / "server.json").read_bytes()

    with pytest.raises(module.PublishError, match="npm/simplicio/package.json " + message):
        _update_public_metadata(module)

    assert (tmp_path / "server.json").read_bytes() == before


def test_public_publisher_moves_the_flow_to_the_release_version(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_version", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    committed = _committed_flow_text()
    current = json.loads(committed)["version"]
    old_line = '  "version": "%s",' % current
    assert current != "3.8.31"
    assert committed.count(old_line) == 1

    changed = _update_public_metadata(module)

    path = tmp_path / FLOW_SOURCE
    assert path in changed
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == "3.8.31"
    # Only the version value changes: the hand formatting of the nodes and the
    # edges survives, so the source stays reviewable as a diff.
    expected = committed.replace(old_line, '  "version": "3.8.31",')
    assert path.read_bytes() == expected.encode("utf-8")


def test_public_publisher_stages_only_the_flow_files_that_changed(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_staging", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)

    changed = _update_public_metadata(module)

    # The generated files are already up to date on a fresh tree, so none of
    # them belongs in the release commit.
    assert _relative_flow_paths(tmp_path, changed) == [FLOW_SOURCE]
    assert len(set(changed)) == len(changed)


def test_public_publisher_regenerates_stale_flow_artifacts(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_regeneration", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    spec = importlib.util.spec_from_file_location("generate_flow_for_contract", ROOT / FLOW_GENERATOR)
    generator = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(generator)
    (tmp_path / FLOW_MERMAID).write_text("stale\n", encoding="utf-8")

    changed = _update_public_metadata(module)

    document = json.loads((tmp_path / FLOW_SOURCE).read_text(encoding="utf-8"))
    assert document["version"] == "3.8.31"
    assert (tmp_path / FLOW_MERMAID).read_bytes() == generator.mermaid(document).encode("utf-8")
    staged = _relative_flow_paths(tmp_path, changed)
    assert FLOW_MERMAID in staged
    assert FLOW_SVG not in staged
    assert FLOW_LANGFLOW not in staged
    # The source comes first and every other flow file follows in sorted order.
    assert staged == [FLOW_SOURCE, FLOW_MERMAID]


def _flow_without_a_version():
    return {key: value for key, value in _committed_flow().items() if key != "version"}


def _flow_text(document, **options):
    return json.dumps(document, ensure_ascii=False, **options) + "\n"


FLOW_NO_VERSION = "docs/flow/simplicio.flow.json has no simplicio.flow/v1 version"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (None, "docs/flow/simplicio.flow.json is missing"),
        ("{not json", "docs/flow/simplicio.flow.json is not valid JSON: "),
        ("[]\n", FLOW_NO_VERSION),
        (_flow_text({**_committed_flow(), "schema": "simplicio.flow/v0"}, indent=2), FLOW_NO_VERSION),
        (_flow_text(_flow_without_a_version(), indent=2), FLOW_NO_VERSION),
        (_flow_text({**_committed_flow(), "version": 3}, indent=2), FLOW_NO_VERSION),
        (
            _flow_text(_committed_flow()),
            'docs/flow/simplicio.flow.json must carry its version on one two-space "version" line '
            "so that only the version changes",
        ),
    ],
    ids=[
        "missing-file",
        "invalid-json",
        "not-an-object",
        "wrong-schema",
        "no-version-key",
        "version-is-not-a-string",
        "version-not-on-its-own-two-space-line",
    ],
)
def test_public_publisher_fails_closed_on_a_flow_source_it_cannot_rewrite(tmp_path, monkeypatch, body, message):
    module = _load_publisher("publish_release_local_flow_closed", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    path = tmp_path / FLOW_SOURCE
    if body is None:
        path.unlink()
    else:
        path.write_bytes(body.encode("utf-8"))
    before = _flow_tree(tmp_path)

    with pytest.raises(module.PublishError, match=re.escape(message)):
        _update_public_metadata(module)

    # A refused update must neither edit the source nor regenerate anything.
    assert _flow_tree(tmp_path) == before
    assert path.exists() is (body is not None)


def test_public_publisher_fails_closed_when_the_flow_generator_is_missing(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_no_generator", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    (tmp_path / FLOW_GENERATOR).unlink()
    before = _flow_tree(tmp_path)

    with pytest.raises(
        module.PublishError,
        match=re.escape("scripts/generate_flow.py is missing, so the flow artifacts cannot be regenerated"),
    ):
        _update_public_metadata(module)

    assert _flow_tree(tmp_path) == before


def _flow_node_path_the_publisher_does_not_touch():
    owned = {
        "README.md", "MCP-CONNECT.md", "VERSION.md", "SIMPLICIO_ECOSYSTEM.md", "server.json",
        "version.txt", FLOW_GENERATOR, *PUBLIC_METADATA_WRAPPERS, *PUBLIC_METADATA_DESKTOP_FILES,
    }
    candidates = [
        path for path in _flow_node_paths(_committed_flow())
        if path not in owned and not path.startswith("docs/flow/")
    ]
    assert candidates, "the committed flow names no source that the publisher leaves alone"
    return candidates[0]


def test_public_publisher_restores_the_flow_when_the_generator_refuses_it(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_refused", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    missing = _flow_node_path_the_publisher_does_not_touch()
    (tmp_path / missing).unlink()
    before = _flow_tree(tmp_path)

    with pytest.raises(module.PublishError, match="flow artifacts could not be regenerated") as refused:
        _update_public_metadata(module)

    # The generator names the missing path, and the source is back at its old
    # version although it was already rewritten when the generator ran.
    assert "flow: missing source " + missing in str(refused.value)
    assert _flow_tree(tmp_path) == before
    assert json.loads((tmp_path / FLOW_SOURCE).read_text(encoding="utf-8"))["version"] == _committed_flow()["version"]


def test_public_publisher_restores_regenerated_flow_files_when_the_final_check_fails(tmp_path, monkeypatch):
    module = _load_publisher("publish_release_local_flow_drift", tmp_path, monkeypatch)
    _write_public_metadata_tree(tmp_path)
    (tmp_path / FLOW_MERMAID).write_text("stale\n", encoding="utf-8")
    shutil.rmtree(tmp_path / "docs/flow/langflow")
    before = _flow_tree(tmp_path)
    real_run = module.run
    commands = []

    def run_with_a_failing_check(command, **options):
        commands.append(list(command))
        if "--check" in command:
            raise module.PublishError("flow drift: simulated")
        return real_run(command, **options)

    monkeypatch.setattr(module, "run", run_with_a_failing_check)

    with pytest.raises(
        module.PublishError,
        match=re.escape("flow artifacts could not be regenerated: flow drift: simulated"),
    ):
        _update_public_metadata(module)

    # The generator ran for real and rewrote the stale file and created the
    # Langflow document before the check refused; all of it is rolled back.
    assert [command[-1] for command in commands] == [str(tmp_path / FLOW_GENERATOR), "--check"]
    assert _flow_tree(tmp_path) == before
    assert not (tmp_path / "docs/flow/langflow").exists()


def test_public_runbook_requires_manual_publication_without_actions():
    source = (ROOT / "docs/RELEASE_RUNBOOK.md").read_text(encoding="utf-8")
    assert "publish-pypi.yml" not in source
    assert "GitHub Actions" not in source
    assert "publicador local/manual" in source


def test_publication_cleanliness_ignores_only_protected_local_state():
    script = ROOT / "scripts/publish_release_local.py"
    spec = importlib.util.spec_from_file_location("publish_release_local", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.is_ignored_local_state(".simplicio/runtime-resource-map.json")
    assert module.is_ignored_local_state("pypi/simplicio/build/generated.whl")
    assert module.is_ignored_local_state(r".simplicio\\ledger\\events.jsonl")
    assert not module.is_ignored_local_state("README.md")
    assert not module.is_ignored_local_state("pypi/simplicio/pyproject.toml")
    source = script.read_text(encoding="utf-8")
    assert "public_preflight(tag, version, require_clean=True)" in source
