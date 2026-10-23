from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import threading
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parents[1]
FLOW = ROOT / "docs/flow/simplicio.flow.json"
MMD = ROOT / "docs/flow/simplicio.mmd"
SVG = ROOT / "docs/flow/simplicio.svg"
LANGFLOW = ROOT / "docs/flow/langflow/simplicio.langflow.json"
FLOW_DOCS = ROOT / "docs/flow/README.md"
VERIFIER = ROOT / "scripts/verify_flow_langflow.py"


def _generator():
    spec = importlib.util.spec_from_file_location("generate_flow", ROOT / "scripts/generate_flow.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _flow() -> dict:
    return json.loads(FLOW.read_text(encoding="utf-8"))


def _verifier():
    spec = importlib.util.spec_from_file_location("verify_flow_langflow", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run_verifier(base_url: str) -> tuple[int, dict]:
    module = _verifier()
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = module.verify(base_url, LANGFLOW, 5.0, False)
    return code, json.loads(buffer.getvalue())


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for child in value.values():
            found |= _keys(child)
        return found
    if isinstance(value, list):
        found: set[str] = set()
        for child in value:
            found |= _keys(child)
        return found
    return set()


def test_flow_sources_exist_and_edges_are_valid():
    module = _generator()
    data = module.load()  # validates sources, artifacts, duplicate/self edges and cycles
    assert data["schema"] == "simplicio.flow/v1"
    assert data["nodes"] and data["edges"]
    ids = [node["id"] for node in data["nodes"]]
    assert len(ids) == len(set(ids))
    assert {node["kind"] for node in data["nodes"]} == {"input", "step", "output"}
    known = set(ids)
    pairs = [tuple(edge) for edge in data["edges"]]
    assert len(pairs) == len(set(pairs))
    for source, target in pairs:
        assert source in known and target in known
        assert source != target


def test_generated_artifacts_are_current_and_deterministic():
    module = _generator()
    data = module.load()
    outputs = {
        MMD: module.mermaid(data),
        SVG: module.svg(data),
        LANGFLOW: module.langflow(data),
    }
    for path, expected in outputs.items():
        assert path.is_file(), path
        assert path.read_text(encoding="utf-8") == expected, path
    # A second generation from the same source must be byte-identical.
    assert module.mermaid(data) == outputs[MMD]
    assert module.svg(data) == outputs[SVG]
    assert module.langflow(data) == outputs[LANGFLOW]


def test_langflow_document_shape_matches_flow_contract():
    module = _generator()
    data = _flow()
    document = json.loads(LANGFLOW.read_text(encoding="utf-8"))

    assert module.validate_langflow_document(document) == []
    assert document["is_component"] is False
    assert document["flow_type"] == "workflow"
    assert document["endpoint_name"] is None
    assert document["access_type"] == "PRIVATE"

    nodes = document["data"]["nodes"]
    edges = document["data"]["edges"]
    assert [node["id"] for node in nodes] == [node["id"] for node in data["nodes"]]
    assert {(edge["source"], edge["target"]) for edge in edges} == {tuple(edge) for edge in data["edges"]}

    for node in nodes:
        assert node["type"] == "genericNode"
        assert node["data"]["id"] == node["id"]
        assert node["data"]["type"].startswith("Simplicio")
        definition = node["data"]["node"]
        assert definition["display_name"]
        assert definition["template"] == {} or "input" in definition["template"]
        assert [output["name"] for output in definition["outputs"]] == ["output"]

    for edge in edges:
        assert edge["sourceHandle"] == module._handle_id(edge["data"]["sourceHandle"])
        assert edge["targetHandle"] == module._handle_id(edge["data"]["targetHandle"])
        assert edge["sourceHandle"].startswith("{") and edge["targetHandle"].startswith("{")

    assert not (module.VOLATILE_KEYS & _keys(document))
    assert "updated_at" not in _keys(document)
    assert "date_created" not in _keys(document)
    assert "version_token" not in _keys(document)


def test_langflow_ids_and_edges_are_stable():
    module = _generator()
    data = _flow()
    first = json.loads(module.langflow(data))
    second = json.loads(module.langflow(module.load()))
    first_ids = [node["id"] for node in first["data"]["nodes"]]
    second_ids = [node["id"] for node in second["data"]["nodes"]]
    assert first_ids == second_ids == [node["id"] for node in data["nodes"]]
    first_edges = [(edge["id"], edge["source"], edge["target"]) for edge in first["data"]["edges"]]
    assert first_edges == [(edge["id"], edge["source"], edge["target"]) for edge in second["data"]["edges"]]
    assert len({edge[0] for edge in first_edges}) == len(first_edges)


def test_mermaid_and_svg_artifacts_render_the_flow():
    data = _flow()
    mermaid = MMD.read_text(encoding="utf-8")
    assert mermaid.startswith("flowchart LR\n")
    for node in data["nodes"]:
        assert f'{node["id"]}["' in mermaid
    for source, target in data["edges"]:
        assert f"  {source} --> {target}\n" in mermaid
    for kind in ("input", "step", "output"):
        assert f"  classDef {kind} " in mermaid

    root = ET.parse(SVG).getroot()
    assert root.tag.endswith("svg")
    texts = [element.text or "" for element in root.iter() if element.tag.endswith("text")]
    assert any(data["title"] in text for text in texts)
    for node in data["nodes"]:
        assert node["id"] in texts
        assert node["label"] in texts


def test_readmes_embed_the_generated_flow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/flow/simplicio.svg" in readme
    assert "scripts/generate_flow.py" in readme
    assert "docs/flow/README.md" in readme
    assert "verify_flow_langflow.py" in readme

    docs = FLOW_DOCS.read_text(encoding="utf-8")
    assert "scripts/generate_flow.py --check" in docs
    assert "scripts/verify_flow_langflow.py" in docs
    assert "mmdc" in docs
    assert "BLOCKED" in docs


def test_verifier_blocks_without_a_live_langflow():
    code, receipt = _run_verifier("http://127.0.0.1:1")
    assert code == 2
    assert receipt["schema"] == "simplicio.langflow-receipt/v1"
    assert receipt["status"] == "blocked"
    assert receipt["reason"] in {"langflow_unreachable", "langflow_unhealthy", "langflow_auth_required"}
    assert receipt["flow"]["nodes"] == len(_flow()["nodes"])
    assert receipt["flow"]["edges"] == len(_flow()["edges"])
    assert receipt["endpoint"] == {"scheme": "http", "host": "127.0.0.1", "port": 1}
    lowered = json.dumps(receipt).lower()
    assert "api_key" not in lowered
    assert "authorization" not in lowered


def test_verifier_readback_logic_against_stub_server():
    """Exercise the import/read-back assertions against a local stub, not Langflow."""
    document = json.loads(LANGFLOW.read_text(encoding="utf-8"))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep test output quiet
            return

        def _send(self, status: int, payload: object) -> None:
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/v1/flows/":
                return self._send(200, [])
            if self.path == "/api/v1/version":
                return self._send(200, {"version": "stub"})
            if self.path == "/api/v1/flows/stub-flow":
                return self._send(200, {"id": "stub-flow", **document})
            return self._send(404, {"detail": "not found"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            if self.path.startswith("/api/v1/flows/upload/"):
                return self._send(201, {"id": "stub-flow", **document})
            return self._send(404, {"detail": "not found"})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        code, receipt = _run_verifier(f"http://127.0.0.1:{server.server_port}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    assert code == 0, receipt
    assert receipt["status"] == "verified"
    assert receipt["flow_id"] == "stub-flow"
    assert receipt["checks"]["node_ids_match"] is True
    assert receipt["checks"]["edge_pairs_match"] is True
    assert receipt["checks"]["node_labels_match"] is True
