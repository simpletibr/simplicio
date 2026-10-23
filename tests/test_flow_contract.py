from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
FLOW = ROOT / "docs/flow/simplicio.flow.json"


def _generator():
    spec = importlib.util.spec_from_file_location("generate_flow", ROOT / "scripts/generate_flow.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_flow_sources_exist_and_edges_are_valid():
    data = json.loads(FLOW.read_text(encoding="utf-8"))
    assert data["schema"] == "simplicio.flow/v1"
    ids = {node["id"] for node in data["nodes"]}
    assert len(ids) == len(data["nodes"])
    for node in data["nodes"]:
        if "source" in node:
            assert (ROOT / node["source"]).exists(), node
    for source, target in data["edges"]:
        assert source in ids and target in ids


def test_generated_artifacts_are_current_and_deterministic():
    module = _generator()
    data = module.load()
    outputs = {
        ROOT / "docs/flow/simplicio.mmd": module.mermaid(data),
        ROOT / "docs/flow/simplicio.svg": module.svg(data),
        ROOT / "docs/flow/langflow/simplicio.langflow.json": module.langflow(data),
    }
    for path, expected in outputs.items():
        assert path.is_file(), path
        assert path.read_text(encoding="utf-8") == expected, path
    assert module.mermaid(module.load()) == outputs[ROOT / "docs/flow/simplicio.mmd"]


def test_readme_embeds_the_generated_flow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/flow/simplicio.svg" in readme
    assert "scripts/generate_flow.py" in readme
