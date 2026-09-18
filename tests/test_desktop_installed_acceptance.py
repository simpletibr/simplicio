from __future__ import annotations

from copy import deepcopy

from scripts.verify_desktop_installed_acceptance import CHECKS, SCHEMA, verify_evidence


def valid_document() -> dict:
    observation = {
        "schema": "simplicio.provider-quotas/v2",
        "status": "available",
        "providers": [
            {
                "id": "codex",
                "source": "codex_app_server",
                "accountScope": "local_authenticated_account",
                "redacted": True,
                "status": "fresh",
                "window_count": 1,
            },
            {
                "id": "grok",
                "source": "grok_cli_billing",
                "accountScope": "local_cli_session",
                "redacted": True,
                "status": "unavailable",
                "window_count": 0,
            },
        ],
    }
    checks = []
    for check_id in CHECKS:
        record = {
            "id": check_id,
            "status": "verified",
            "source": "installed",
            "redacted": True,
            "evidence_id": f"evidence-{check_id}",
        }
        if check_id == "provider_quotas_contract":
            record["observation"] = observation
        if check_id == "provider_quotas_current":
            record["fresh_provider_ids"] = ["codex"]
        if check_id == "host_plugin_freshness":
            record["observation"] = {
                "schema": "simplicio.host-plugin-freshness/v1",
                "receipt": "present",
                "catalog_compared": False,
                "hosts": [
                    {
                        "id": "codex",
                        "status": "verified",
                        "freshness": "current",
                        "verification": "installed_tree_and_manager",
                    },
                    {
                        "id": "claude",
                        "status": "unknown",
                        "freshness": "unknown",
                        "verification": "none",
                    },
                ],
            }
        checks.append(record)
    return {
        "schema": SCHEMA,
        "source": "installed",
        "preview": False,
        "clean_home": True,
        "platform": "linux-x64",
        "installed_app": {
            "version": "3.8.47",
            "runtime_version": "3.8.47",
            "runtime_digest": "a" * 64,
        },
        "checks": checks,
    }


def test_complete_installed_acceptance_is_ready() -> None:
    report = verify_evidence(valid_document())
    assert report["ready"] is True
    assert report["verified_checks"] == list(CHECKS)


def test_blocked_install_is_explicit_but_not_ready() -> None:
    document = valid_document()
    document["checks"][4] = {
        "id": "signed_update_download",
        "status": "blocked",
        "source": "installed",
        "redacted": True,
        "evidence_id": "update-download-blocked",
        "reason_code": "signed_sidecar_missing",
    }
    report = verify_evidence(document)
    assert report["ready"] is False
    assert report["blocked_checks"] == ["signed_update_download"]
    assert report["errors"] == []


def test_preview_and_missing_current_quota_are_not_passes() -> None:
    document = valid_document()
    document["preview"] = True
    current = document["checks"][3]
    current.pop("fresh_provider_ids")
    report = verify_evidence(document)
    codes = {item["code"] for item in report["errors"]}
    assert {"installed_source_required", "quota_current_missing"} <= codes


def test_quota_identity_and_root_state_are_checked() -> None:
    document = valid_document()
    observation = document["checks"][2]["observation"]
    observation["status"] = "unavailable"
    observation["providers"][0]["source"] = "grok_cli_billing"
    report = verify_evidence(document)
    codes = {item["code"] for item in report["errors"]}
    assert {"quota_provider_identity_invalid", "quota_root_status_mismatch"} <= codes


def test_sensitive_evidence_is_rejected() -> None:
    document = deepcopy(valid_document())
    document["checks"][0]["raw_output"] = "not publishable"
    report = verify_evidence(document)
    assert report["errors"][0]["code"] == "sensitive_field"
    path_document = deepcopy(valid_document())
    path_document["config_path"] = "/private/home"
    assert verify_evidence(path_document)["errors"][0]["code"] == "sensitive_field"


def test_clean_home_and_window_count_are_not_secret_fields() -> None:
    report = verify_evidence(valid_document())
    assert report["ready"] is True
    assert report["errors"] == []


def test_unknown_host_plugin_receipt_cannot_be_current() -> None:
    document = valid_document()
    freshness = next(check for check in document["checks"] if check["id"] == "host_plugin_freshness")
    freshness["observation"]["hosts"][0]["status"] = "unknown"
    freshness["observation"]["hosts"][0]["freshness"] = "current"
    codes = {item["code"] for item in verify_evidence(document)["errors"]}
    assert "host_plugin_current_from_unknown" in codes
    freshness["observation"]["receipt"] = "missing"
    freshness["observation"]["hosts"][0]["status"] = "verified"
    codes = {item["code"] for item in verify_evidence(document)["errors"]}
    assert "host_plugin_current_without_receipt" in codes
    freshness["observation"]["receipt"] = "present"
    freshness["observation"]["hosts"][0]["catalog_version"] = "3.8.47"
    codes = {item["code"] for item in verify_evidence(document)["errors"]}
    assert "host_plugin_catalog_version_invented" in codes
