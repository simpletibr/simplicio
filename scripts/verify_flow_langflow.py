#!/usr/bin/env python3
"""Fail-closed Langflow import verification for the generated flow (#441).

Offline shape validation is not proof that Langflow can import the document.
This tool therefore never falls back to a local-only success:

* no Langflow at ``--base-url`` (default ``http://localhost:7860``) prints a
  machine-readable ``blocked`` receipt and exits 2;
* an import that is rejected, or a fetch-back mismatch, prints ``failed`` and
  exits 1;
* only an import followed by a read-back that matches nodes and edges prints
  ``verified`` and exits 0.

Credentials are read from ``LANGFLOW_API_KEY`` when present and are never
written to the receipt or to stdout/logs. ``--api-key-file`` reads the key from
a file so it never appears in ``argv``, ``--evidence`` writes the
credential-free receipt to disk, and ``LANGFLOW_API_KEY_FILE`` points at a key
file for non-interactive runs.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FLOW = ROOT / "docs" / "flow" / "langflow" / "simplicio.langflow.json"
SCHEMA = "simplicio.langflow-receipt/v1"
DEFAULT_BASE_URL = "http://localhost:7860"
API_KEY_ENV = "LANGFLOW_API_KEY"
API_KEY_FILE_ENV = "LANGFLOW_API_KEY_FILE"
EXIT_VERIFIED = 0
EXIT_FAILED = 1
EXIT_BLOCKED = 2

_ACTIVE_API_KEY: str | None = None


def _api_key() -> str | None:
    """Return the credential for this run without ever echoing it."""
    return _ACTIVE_API_KEY or os.environ.get(API_KEY_ENV)


def _load_generator():
    sys.path.insert(0, str(ROOT / "scripts"))
    import generate_flow

    return generate_flow


def _endpoint(base_url: str) -> dict:
    parsed = urllib.parse.urlsplit(base_url)
    try:
        port = parsed.port
    except ValueError:
        port = None
    return {
        "scheme": parsed.scheme or "http",
        "host": parsed.hostname or "",
        "port": port or (443 if parsed.scheme == "https" else 80),
    }


def _redact(value: object) -> object:
    key = _api_key()
    if not key:
        return value
    if isinstance(value, str):
        return value.replace(key, "<redacted>")
    if isinstance(value, dict):
        return {name: _redact(child) for name, child in value.items()}
    if isinstance(value, list):
        return [_redact(child) for child in value]
    return value


def _error_text(exc: BaseException) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    return _redact(text)[:300]


def _request(
    url: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    content_type: str | None = None,
    timeout: float = 10.0,
) -> tuple[int | None, bytes, str | None]:
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    key = _api_key()
    if key:
        headers["x-api-key"] = key
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), None
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), _error_text(exc)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, b"", _error_text(exc)


def _multipart(field: str, filename: str, payload: bytes) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        "Content-Type: application/json\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + payload + tail, f"multipart/form-data; boundary={boundary}"


def _flow_summary(path: Path, document: dict) -> dict:
    data = document.get("data") or {}
    try:
        display_path = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        display_path = path.name
    return {
        "path": display_path,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "nodes": len(data.get("nodes") or []),
        "edges": len(data.get("edges") or []),
    }


def _receipt(status: str, reason: str, endpoint: dict, flow: dict, checks: dict, **extra) -> dict:
    receipt = {
        "schema": SCHEMA,
        "tool": "scripts/verify_flow_langflow.py",
        "status": status,
        "reason": reason,
        "endpoint": endpoint,
        "flow": flow,
        "checks": checks,
    }
    receipt.update(extra)
    return _redact(receipt)


def _blocked(reason: str, endpoint: dict, flow: dict, message: str, checks: dict | None = None, **extra) -> int:
    print(
        json.dumps(
            _receipt(
                "blocked",
                reason,
                endpoint,
                flow,
                checks or {},
                message=message,
                **extra,
            ),
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return EXIT_BLOCKED


def _failed(reason: str, endpoint: dict, flow: dict, message: str, checks: dict | None = None, **extra) -> int:
    print(
        json.dumps(
            _receipt(
                "failed",
                reason,
                endpoint,
                flow,
                checks or {},
                message=message,
                **extra,
            ),
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return EXIT_FAILED


def _node_labels(document: dict) -> dict[str, str]:
    labels = {}
    for node in (document.get("data") or {}).get("nodes") or []:
        node_id = node.get("id")
        definition = (node.get("data") or {}).get("node") or {}
        if isinstance(node_id, str):
            labels[node_id] = definition.get("display_name", "")
    return labels


def _edge_pairs(document: dict) -> set[tuple[str, str]]:
    return {
        (edge.get("source"), edge.get("target"))
        for edge in (document.get("data") or {}).get("edges") or []
        if isinstance(edge, dict)
    }


def verify(base_url: str, flow_path: Path, timeout: float, cleanup: bool, api_key: str | None = None) -> int:
    global _ACTIVE_API_KEY
    _ACTIVE_API_KEY = api_key
    endpoint = _endpoint(base_url)
    if not endpoint["host"]:
        return _failed("invalid_base_url", endpoint, {}, "base URL has no host")
    if not flow_path.is_file():
        return _failed("flow_missing", endpoint, {}, f"flow artifact not found: {flow_path}")
    try:
        expected = json.loads(flow_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _failed("flow_invalid", endpoint, {}, f"flow artifact is not valid JSON: {_error_text(exc)}")
    flow = _flow_summary(flow_path, expected)

    generator = _load_generator()
    errors = generator.validate_langflow_document(expected)
    if errors:
        return _failed("flow_shape_invalid", endpoint, flow, "; ".join(errors[:5]))

    base = base_url.rstrip("/")
    status, _body, error = _request(f"{base}/api/v1/flows/", timeout=timeout)
    if status is None:
        return _blocked(
            "langflow_unreachable",
            endpoint,
            flow,
            "no Langflow server answered /api/v1/flows/; live import was not attempted",
            {"availability_http_status": None, "availability_error": error or "connection failed"},
        )
    if status in (401, 403):
        return _blocked(
            "langflow_auth_required",
            endpoint,
            flow,
            "Langflow is reachable but the API key was rejected or missing; no credential is stored in this receipt",
            {"availability_http_status": status},
        )
    if status != 200:
        return _blocked(
            "langflow_unhealthy",
            endpoint,
            flow,
            "Langflow answered /api/v1/flows/ without a usable response",
            {"availability_http_status": status, "availability_error": error},
        )

    version_status, version_body, _version_error = _request(f"{base}/api/v1/version", timeout=timeout)
    version = None
    if version_status == 200:
        try:
            version_payload = json.loads(version_body)
            version = version_payload.get("version") if isinstance(version_payload, dict) else None
        except json.JSONDecodeError:
            version = None

    payload, content_type = _multipart("file", flow_path.name, flow_path.read_bytes())
    import_status, import_body, import_error = _request(
        f"{base}/api/v1/flows/upload/",
        method="POST",
        body=payload,
        content_type=content_type,
        timeout=timeout,
    )
    checks = {"availability_http_status": status, "import_http_status": import_status}
    if import_status is None:
        return _blocked(
            "langflow_import_unreachable",
            endpoint,
            flow,
            "Langflow answered the listing but the import request failed",
            checks | {"import_error": import_error or "connection failed"},
            langflow={"version": version},
        )
    if import_status in (401, 403):
        return _blocked(
            "langflow_auth_required",
            endpoint,
            flow,
            "Langflow rejected the import without valid credentials",
            checks,
            langflow={"version": version},
        )
    if import_status in (404, 405):
        return _blocked(
            "langflow_import_endpoint_unavailable",
            endpoint,
            flow,
            "this Langflow build has no /api/v1/flows/upload/ endpoint; live import was not verified",
            checks,
            langflow={"version": version},
        )
    if import_status not in (200, 201):
        return _failed(
            "langflow_import_rejected",
            endpoint,
            flow,
            f"Langflow rejected the flow import (HTTP {import_status})",
            checks | {"import_error": import_error},
            langflow={"version": version},
        )
    try:
        imported = json.loads(import_body)
    except json.JSONDecodeError:
        return _failed("langflow_import_response_invalid", endpoint, flow, "import response was not JSON", checks)
    if isinstance(imported, list):
        imported = imported[0] if imported else None
    if not isinstance(imported, dict):
        return _failed("langflow_import_response_invalid", endpoint, flow, "import response was not a flow object", checks)
    flow_id = imported.get("id") or imported.get("flow_id")
    if not isinstance(flow_id, str) or not flow_id:
        return _failed("langflow_import_response_invalid", endpoint, flow, "import response carried no flow id", checks)

    fetch_status, fetch_body, fetch_error = _request(f"{base}/api/v1/flows/{flow_id}", timeout=timeout)
    checks["fetch_http_status"] = fetch_status
    if fetch_status != 200:
        return _failed(
            "langflow_readback_failed",
            endpoint,
            flow,
            f"could not read the imported flow back (HTTP {fetch_status})",
            checks | {"fetch_error": fetch_error},
            flow_id=flow_id,
            langflow={"version": version},
        )
    try:
        fetched = json.loads(fetch_body)
    except json.JSONDecodeError:
        return _failed("langflow_readback_invalid", endpoint, flow, "read-back response was not JSON", checks, flow_id=flow_id)
    if not isinstance(fetched, dict):
        return _failed(
            "langflow_readback_invalid",
            endpoint,
            flow,
            "read-back response was not a flow object",
            checks,
            flow_id=flow_id,
        )

    expected_nodes = (expected.get("data") or {}).get("nodes") or []
    expected_edges = _edge_pairs(expected)
    expected_ids = sorted(node["id"] for node in expected_nodes)
    fetched_nodes = (fetched.get("data") or {}).get("nodes") or []
    fetched_ids = sorted(node.get("id") for node in fetched_nodes if isinstance(node, dict))
    fetched_edges = _edge_pairs(fetched)
    nodes_match = expected_ids == fetched_ids
    edges_match = expected_edges == fetched_edges
    labels_match = _node_labels(expected) == _node_labels(fetched)
    checks.update(
        {
            "expected_nodes": len(expected_ids),
            "imported_nodes": len(fetched_ids),
            "expected_edges": len(expected_edges),
            "imported_edges": len(fetched_edges),
            "node_ids_match": nodes_match,
            "node_labels_match": labels_match,
            "edge_pairs_match": edges_match,
        }
    )
    if not (nodes_match and edges_match and labels_match):
        return _failed(
            "langflow_readback_mismatch",
            endpoint,
            flow,
            "the read-back flow does not match the generated nodes/edges",
            checks,
            flow_id=flow_id,
            langflow={"version": version},
        )

    receipt = _receipt(
        "verified",
        "langflow_import_verified",
        endpoint,
        flow,
        checks,
        flow_id=flow_id,
        langflow={"version": version},
        cleaned_up=False,
    )
    if cleanup:
        delete_status, _delete_body, _delete_error = _request(
            f"{base}/api/v1/flows/{flow_id}", method="DELETE", timeout=timeout
        )
        receipt["cleanup"] = {"http_status": delete_status, "removed": delete_status in (200, 204)}
        receipt["cleaned_up"] = receipt["cleanup"]["removed"]
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return EXIT_VERIFIED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Langflow base URL (default: %(default)s)")
    parser.add_argument("--flow", type=Path, default=DEFAULT_FLOW, help="generated Langflow flow JSON")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-request timeout in seconds")
    parser.add_argument("--cleanup", action="store_true", help="delete the imported flow after a verified read-back")
    parser.add_argument(
        "--api-key-file",
        type=Path,
        default=None,
        help=f"read the API key from this file instead of {API_KEY_ENV} (keeps it out of argv)",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=None,
        help="write the JSON receipt (pretty-printed, credential-free) to this path",
    )
    args = parser.parse_args(argv)
    api_key = None
    key_file = args.api_key_file
    if key_file is None and os.environ.get(API_KEY_FILE_ENV):
        key_file = Path(os.environ[API_KEY_FILE_ENV])
    if key_file is not None:
        try:
            api_key = key_file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            print(
                json.dumps(
                    _receipt(
                        "blocked",
                        "api_key_file_unreadable",
                        _endpoint(args.base_url),
                        {},
                        {},
                        message=f"could not read --api-key-file: {exc.__class__.__name__}",
                    ),
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return EXIT_BLOCKED
        if not api_key:
            return _blocked("api_key_file_empty", _endpoint(args.base_url), {}, "--api-key-file is empty")
    if args.evidence is None:
        return verify(args.base_url, args.flow, args.timeout, args.cleanup, api_key)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = verify(args.base_url, args.flow, args.timeout, args.cleanup, api_key)
    payload = buffer.getvalue()
    try:
        receipt = json.loads(payload)
    except json.JSONDecodeError:
        sys.stdout.write(payload)
        return code
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
