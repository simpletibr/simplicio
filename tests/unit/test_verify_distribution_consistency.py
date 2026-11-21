"""Unit tests for scripts/verify_distribution_consistency.py.

Coverage intent (see issue #8 acceptance criteria):
- happy path (all sources agree) exits 0 with no ERROR findings
- each ERROR-producing drift is exercised in isolation
- each WARN-producing drift is exercised in isolation
- parser helpers raise on malformed input (error/edge cases)
- the beta-date check is deterministic: real wall-clock time is never
  read directly by a test — we freeze `date.today()` via monkeypatch.

No test touches the network, a real clock, or global state outside of its
own tmp_path repo tree, satisfying the "no test depends on network, real
clock, or unisolated global state" acceptance criterion.
"""
from __future__ import annotations

import datetime as real_datetime
import json

import pytest


def run_main(module, repo, capsys):
    exit_code = module.main(["--root", str(repo.root)])
    captured = capsys.readouterr().out
    return exit_code, captured


def freeze_today(monkeypatch, module, iso_date: str) -> None:
    frozen = real_datetime.date.fromisoformat(iso_date)

    class _FrozenDate(real_datetime.date):
        @classmethod
        def today(cls):
            return frozen

    monkeypatch.setattr(module, "date", _FrozenDate)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_happy_path_all_consistent_exits_zero(verify_module, repo, monkeypatch, capsys):
    freeze_today(monkeypatch, verify_module, "2020-01-01")  # well before beta_until
    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "[ERROR]" not in out
    assert "0 error(s)" in out
    assert "all public install references use the canonical `master` branch" in out
    assert "release version sources agree on 3.5.2" in out
    assert "wrapper/package versions match the release manifest" in out
    assert "MCP registry entry server.json agrees with the manifest" in out
    assert "flow source docs/flow/simplicio.flow.json carries the manifest version 3.5.2" in out


# ---------------------------------------------------------------------------
# ERROR cases
# ---------------------------------------------------------------------------


def test_version_md_missing_master_clause_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_version_md_missing_master_clause()
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "no longer declares `master` as canonical branch" in out


@pytest.mark.parametrize(
    "filename", ["README.md", "INSTALL.md", "install.sh", "install.ps1"]
)
def test_main_branch_reference_is_error(verify_module, repo, monkeypatch, capsys, filename):
    repo.with_main_branch_reference(filename)
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "install references point at `/main/`" in out
    assert filename in out


def test_version_txt_manifest_mismatch_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_version_txt("9.9.9")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "version mismatch: version.txt=9.9.9 but manifest=3.5.2" in out


# ---------------------------------------------------------------------------
# ERROR cases: the official MCP registry entry (server.json)
# ---------------------------------------------------------------------------


def registry_findings(module, repo):
    return [item for item in module.run_audit(repo.root) if "server.json" in item.message]


def test_registry_entry_in_agreement_is_one_ok_finding(verify_module, repo):
    findings = registry_findings(verify_module, repo)

    assert [item.level for item in findings] == ["OK"]


def test_registry_entry_with_a_stale_top_level_version_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_server_json(version="3.5.1")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json version 3.5.1 differs from the manifest version 3.5.2" in out


def test_registry_entry_with_a_stale_package_version_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_server_json_package(version="3.5.1")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json package @simpletibr/simplicio version 3.5.1 differs from the manifest version 3.5.2" in out


def test_registry_entry_name_that_differs_from_mcp_name_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_server_json(name="io.github.someone-else/simplicio")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json name 'io.github.someone-else/simplicio' differs from the mcpName" in out


@pytest.mark.parametrize("mcp_name", [None, ""])
def test_wrapper_without_mcp_name_is_error(verify_module, repo, monkeypatch, capsys, mcp_name):
    path = repo.root / "npm/simplicio/package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("mcpName")
    if mcp_name is not None:
        data["mcpName"] = mcp_name
    path.write_text(json.dumps(data), encoding="utf-8")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "npm/simplicio/package.json has no mcpName" in out


def test_registry_entry_without_a_package_for_the_wrapper_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_server_json_package(identifier="@someone-else/simplicio")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json has no package entry for the npm wrapper @simpletibr/simplicio" in out


@pytest.mark.parametrize("packages", [None, [], ["@simpletibr/simplicio"]])
def test_registry_entry_without_usable_packages_is_error(verify_module, repo, monkeypatch, capsys, packages):
    repo.with_server_json(packages=packages)
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json has no package entry for the npm wrapper" in out


def test_wrapper_without_a_name_is_error_instead_of_matching_a_nameless_entry(verify_module, repo, monkeypatch, capsys):
    repo.with_npm_manifest(name=None)
    repo.with_server_json_package(identifier=None)
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "npm/simplicio/package.json has no name" in out


def test_registry_entry_without_a_version_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_server_json(version=None)
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json version None differs from the manifest version 3.5.2" in out


def test_missing_registry_entry_is_error(verify_module, repo, monkeypatch, capsys):
    (repo.root / "server.json").unlink()
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json (official MCP registry entry) is missing" in out


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("{not json", "is not valid JSON"),
        ("", "is not valid JSON"),
        ("[]", "is not a JSON object"),
        ("\"text\"", "is not a JSON object"),
    ],
)
def test_registry_entry_that_is_not_a_json_object_is_error(verify_module, repo, monkeypatch, capsys, body, message):
    (repo.root / "server.json").write_text(body, encoding="utf-8")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "server.json (official MCP registry entry) " + message in out


def test_registry_entry_is_not_hidden_by_wrapper_version_lag_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_npm_version("simplicio", "1.0.0")
    repo.with_server_json(version="1.0.0")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    # The registry entry follows the release manifest, not the lagging wrapper.
    assert exit_code == 1
    assert "server.json version 1.0.0 differs from the manifest version 3.5.2" in out


def test_several_registry_problems_are_reported_in_one_finding(verify_module, repo):
    repo.with_server_json(version="3.5.1", name="io.github.someone-else/simplicio")

    findings = registry_findings(verify_module, repo)

    assert [item.level for item in findings] == ["ERROR"]
    assert "version 3.5.1 differs" in findings[0].message
    assert "name 'io.github.someone-else/simplicio' differs" in findings[0].message


# ---------------------------------------------------------------------------
# ERROR cases: the flow source (docs/flow/simplicio.flow.json)
# ---------------------------------------------------------------------------


def flow_findings(module, repo):
    return [item for item in module.run_audit(repo.root) if "docs/flow/simplicio.flow.json" in item.message]


def test_flow_source_in_agreement_is_one_ok_finding(verify_module, repo):
    findings = flow_findings(verify_module, repo)

    assert [item.level for item in findings] == ["OK"]


def test_flow_source_with_a_stale_version_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_flow(version="3.10.0")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "flow source docs/flow/simplicio.flow.json version 3.10.0 differs from the manifest version 3.5.2" in out


def test_flow_source_without_a_version_is_error(verify_module, repo, monkeypatch, capsys):
    repo.with_flow(version=None)
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "flow source docs/flow/simplicio.flow.json version None differs from the manifest version 3.5.2" in out


def test_missing_flow_source_is_error(verify_module, repo, monkeypatch, capsys):
    (repo.root / "docs/flow/simplicio.flow.json").unlink()
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "docs/flow/simplicio.flow.json (flow source) is missing" in out


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("{not json", "is not valid JSON"),
        ("", "is not valid JSON"),
        ("[]", "is not a JSON object"),
        ("\"text\"", "is not a JSON object"),
    ],
)
def test_flow_source_that_is_not_a_json_object_is_error(verify_module, repo, monkeypatch, capsys, body, message):
    (repo.root / "docs/flow/simplicio.flow.json").write_text(body, encoding="utf-8")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 1
    assert "docs/flow/simplicio.flow.json (flow source) " + message in out


def test_flow_source_is_not_hidden_by_wrapper_version_lag_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_npm_version("simplicio", "1.0.0")
    repo.with_flow(version="1.0.0")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    # The flow source follows the release manifest, not the lagging wrapper.
    assert exit_code == 1
    assert "flow source docs/flow/simplicio.flow.json version 1.0.0 differs from the manifest version 3.5.2" in out


# ---------------------------------------------------------------------------
# WARN cases (non-fatal drift)
# ---------------------------------------------------------------------------


def test_wrapper_version_drift_is_warning_not_error(verify_module, repo, monkeypatch, capsys):
    repo.with_npm_version("simplicio", "1.0.0")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0  # warnings alone must not fail the build
    assert "wrapper versions lag manifest 3.5.2" in out
    assert "npm/simplicio/package.json=1.0.0" in out


def test_ecosystem_doc_version_drift_is_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_ecosystem_version("1.0.0 (package.json)")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "SIMPLICIO_ECOSYSTEM.md advertises" in out


def test_stale_beta_until_is_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_beta_until("2020-06-30")
    freeze_today(monkeypatch, verify_module, "2020-07-14")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "public-beta date 2020-06-30 is before" in out


def test_beta_until_not_yet_stale_produces_no_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_beta_until("2099-06-30")
    freeze_today(monkeypatch, verify_module, "2020-07-14")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "is before" not in out


def test_unparseable_beta_until_is_warning(verify_module, repo, monkeypatch, capsys):
    repo.with_beta_until("not-a-date")
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "could not parse beta_until date: not-a-date" in out


def test_readme_beta_no_end_date_contradicts_manifest(verify_module, repo, monkeypatch, capsys):
    repo.with_beta_until("2099-06-30")
    repo.with_readme_beta_no_end_date()
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    assert exit_code == 0
    assert "README has no-end-date claim but manifest carries beta_until=2099-06-30" in out


def test_no_beta_no_end_date_warning_when_no_beta_until(verify_module, repo, monkeypatch, capsys):
    repo.with_manifest(entitlement={})
    repo.with_readme_beta_no_end_date()
    freeze_today(monkeypatch, verify_module, "2020-01-01")

    exit_code, out = run_main(verify_module, repo, capsys)

    # No beta_until at all means nothing to contradict.
    assert exit_code == 0
    assert "README has no-end-date claim" not in out


# ---------------------------------------------------------------------------
# Parser helper edge/error cases
# ---------------------------------------------------------------------------


def test_version_from_pyproject_parses_version(verify_module, tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\nversion = "4.5.6"\n', encoding="utf-8")

    assert verify_module.version_from_pyproject(path) == "4.5.6"


def test_version_from_pyproject_raises_when_unparseable(verify_module, tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project]\nname = "x"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="could not parse pyproject version"):
        verify_module.version_from_pyproject(path)


def test_version_from_package_json_reads_version_field(verify_module, tmp_path):
    path = tmp_path / "package.json"
    path.write_text(json.dumps({"version": "7.8.9", "name": "x"}), encoding="utf-8")

    assert verify_module.version_from_package_json(path) == "7.8.9"


def test_iter_install_reference_files_yields_root_relative_paths(verify_module, tmp_path):
    # The kept implementation threads an explicit `root` argument through
    # (see iter_install_reference_files(root) / run_audit(root)) instead of
    # a module-level `rel()` helper over a mutated global `ROOT` — that
    # global-state design was dropped when the two implementations were
    # merged; this test covers the surviving equivalent behavior instead.
    (tmp_path / "READMEs").mkdir()
    fixed_names = {
        "README.md",
        "INSTALL.md",
        "install.sh",
        "install.ps1",
        "pypi/simplicio/simplicio/__main__.py",
    }
    for relative in fixed_names:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    paths = list(verify_module.iter_install_reference_files(tmp_path))
    assert {str(p.relative_to(tmp_path)).replace("\\", "/") for p in paths} == fixed_names
