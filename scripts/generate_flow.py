#!/usr/bin/env python3
"""Generate Mermaid/SVG/Langflow artifacts from docs/flow/simplicio.flow.json.

The JSON is the single source of truth. Generation is deterministic: the same
input bytes produce the same output bytes, with no timestamps, random ids or
host-specific data. Every non-artifact source must exist in the repository;
drift fails before writing anything.

The Langflow document follows the import shape used by Langflow 1.x exports:
``{name, description, data: {nodes, edges}, ...}`` with ``genericNode`` React
Flow wrappers and handle objects carried both in ``data`` and in the scaped
handle strings. It is a conceptual map, not an executable pipeline; live import
is verified separately by ``scripts/verify_flow_langflow.py``.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / "docs" / "flow" / "simplicio.flow.json"
OUT = FLOW.parent
KINDS = ("input", "step", "output")
COLORS = {"input": "#e8f1ff", "step": "#fff7d6", "output": "#e8f7ea"}
STROKES = {"input": "#3b6fb6", "step": "#b38b00", "output": "#2f7d32"}

LANGFLOW_LF_VERSION = "1.12.0"
LANGFLOW_COMPONENT = {
    "input": "SimplicioInput",
    "step": "SimplicioStep",
    "output": "SimplicioOutput",
}
LANGFLOW_NODE_WIDTH = 320
LANGFLOW_NODE_HEIGHT = 96
# Langflow's scapedJSONStringfy replaces every double quote with this marker.
LANGFLOW_QUOTE_MARKER = "\u0153"
VOLATILE_KEYS = {"updated_at", "date_created", "last_tested_version", "version_token"}


def load() -> dict:
    data = json.loads(FLOW.read_text(encoding="utf-8"))
    if data.get("schema") != "simplicio.flow/v1":
        raise SystemExit("flow: unsupported schema")
    nodes = data.get("nodes", [])
    ids = [node.get("id") for node in nodes]
    if not ids or len(ids) != len(set(ids)):
        raise SystemExit("flow: node ids must be unique and non-empty")
    for node in nodes:
        if not isinstance(node.get("id"), str) or not node["id"]:
            raise SystemExit("flow: node ids must be unique and non-empty")
        if node.get("kind") not in KINDS:
            raise SystemExit(f"flow: invalid node kind {node.get('kind')!r}")
        source = node.get("source")
        if source and not (ROOT / source).exists():
            raise SystemExit(f"flow: missing source {source}")
        artifact = node.get("artifact")
        if artifact and not (ROOT / artifact).exists():
            raise SystemExit(f"flow: missing artifact {artifact}")
    known = set(ids)
    edges = data.get("edges", [])
    pairs = [tuple(edge) for edge in edges]
    if len(pairs) != len(set(pairs)):
        raise SystemExit("flow: duplicate edges")
    for edge in edges:
        if len(edge) != 2 or edge[0] not in known or edge[1] not in known:
            raise SystemExit(f"flow: invalid edge {edge!r}")
        if edge[0] == edge[1]:
            raise SystemExit(f"flow: self edge {edge!r}")
    _assert_acyclic(ids, pairs)
    return data


def _assert_acyclic(ids: list[str], edges: list[tuple[str, str]]) -> None:
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in ids}
    for source, target in edges:
        outgoing[source].append(target)
    state: dict[str, int] = {}

    def visit(node_id: str) -> None:
        state[node_id] = 1
        for target in outgoing[node_id]:
            if state.get(target) == 1:
                raise SystemExit(f"flow: cycle through {node_id} -> {target}")
            if state.get(target, 0) == 0:
                visit(target)
        state[node_id] = 2

    for node_id in ids:
        if state.get(node_id, 0) == 0:
            visit(node_id)


def _depths(data: dict) -> dict[str, int]:
    """Longest-path depth per node, in source order for a stable layout."""
    order = [node["id"] for node in data["nodes"]]
    incoming: dict[str, list[str]] = {node_id: [] for node_id in order}
    for source, target in data["edges"]:
        incoming[target].append(source)
    depth: dict[str, int] = {}

    def resolve(node_id: str) -> int:
        if node_id not in depth:
            depth[node_id] = max((resolve(parent) + 1 for parent in incoming[node_id]), default=0)
        return depth[node_id]

    for node_id in order:
        resolve(node_id)
    return depth


def mermaid(data: dict) -> str:
    lines = ["flowchart LR"]
    for node in data["nodes"]:
        label = node["label"].replace('"', "'")
        lines.append(f'  {node["id"]}["{label}"]')
    for source, target in data["edges"]:
        lines.append(f"  {source} --> {target}")
    for kind in KINDS:
        ids = [node["id"] for node in data["nodes"] if node["kind"] == kind]
        if ids:
            lines.append(f"  classDef {kind} fill:{COLORS[kind]},stroke:{STROKES[kind]},stroke-width:1px;")
            lines.append("  class " + ",".join(ids) + f" {kind};")
    return "\n".join(lines) + "\n"


def svg(data: dict) -> str:
    width, height = 1280, 760
    columns = {kind: [n for n in data["nodes"] if n["kind"] == kind] for kind in KINDS}
    positions: dict[str, tuple[int, int]] = {}
    for column, kind in enumerate(KINDS):
        for row, node in enumerate(columns[kind]):
            positions[node["id"]] = (40 + column * 420, 80 + row * 130)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#555"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="40" y="40" font-family="sans-serif" font-size="20" font-weight="700">{html.escape(data["title"])}</text>',
    ]
    for source, target in data["edges"]:
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        parts.append(
            f'<line x1="{x1 + 320}" y1="{y1 + 35}" x2="{x2}" y2="{y2 + 35}" '
            'stroke="#555" stroke-width="1.5" marker-end="url(#arrow)"/>'
        )
    for node in data["nodes"]:
        x, y = positions[node["id"]]
        kind = node["kind"]
        parts.append(
            f'<rect x="{x}" y="{y}" width="320" height="70" rx="10" fill="{COLORS[kind]}" '
            f'stroke="{STROKES[kind]}" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{x + 14}" y="{y + 28}" font-family="sans-serif" font-size="14" '
            f'font-weight="700">{html.escape(node["id"])}</text>'
        )
        parts.append(
            f'<text x="{x + 14}" y="{y + 50}" font-family="sans-serif" font-size="12" '
            f'fill="#333">{html.escape(node["label"])}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _canonical(value: object) -> str:
    """Langflow customStringify: sorted keys, compact separators, no spaces."""
    if isinstance(value, dict):
        pairs = (f'"{key}":{_canonical(value[key])}' for key in sorted(value))
        return "{" + ",".join(pairs) + "}"
    if isinstance(value, list):
        return "[" + ",".join(_canonical(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def _handle_id(handle: dict) -> str:
    return _canonical(handle).replace('"', LANGFLOW_QUOTE_MARKER)


def _source_handle(node: dict) -> dict:
    return {
        "dataType": LANGFLOW_COMPONENT[node["kind"]],
        "id": node["id"],
        "name": "output",
        "output_types": ["Message"],
    }


def _target_handle(node: dict) -> dict:
    return {
        "fieldName": "input",
        "id": node["id"],
        "inputTypes": ["Message"],
        "type": "str",
    }


def _input_field() -> dict:
    return {
        "advanced": False,
        "display_name": "Input",
        "dynamic": False,
        "fileTypes": [],
        "info": "",
        "input_types": ["Message"],
        "list": False,
        "load_from_db": False,
        "multiline": False,
        "name": "input",
        "password": False,
        "placeholder": "",
        "required": False,
        "show": True,
        "title_case": False,
        "trace_as_input": True,
        "type": "str",
        "value": "",
    }


def _langflow_node(node: dict, position: dict, has_input: bool) -> dict:
    component = LANGFLOW_COMPONENT[node["kind"]]
    template = {"input": _input_field()} if has_input else {}
    description = f"{node['kind']} · {node.get('source') or node.get('artifact') or ''}"
    return {
        "id": node["id"],
        "type": "genericNode",
        "position": position,
        "selected": False,
        "dragging": False,
        "measured": {"width": LANGFLOW_NODE_WIDTH, "height": LANGFLOW_NODE_HEIGHT},
        "data": {
            "id": node["id"],
            "type": component,
            "node": {
                "base_classes": ["Message"],
                "beta": False,
                "conditional_paths": [],
                "custom_fields": {},
                "description": description,
                "display_name": node["label"],
                "documentation": node.get("source") or node.get("artifact") or "",
                "edited": False,
                "field_order": sorted(template),
                "frozen": False,
                "icon": "Workflow",
                "legacy": False,
                "lf_version": LANGFLOW_LF_VERSION,
                "metadata": {"component_class_name": component, "module": "simplicio.flow"},
                "output_types": ["Message"],
                "outputs": [
                    {
                        "allows_loop": False,
                        "cache": True,
                        "display_name": "Output",
                        "group_outputs": False,
                        "method": "output_response",
                        "name": "output",
                        "selected": "Message",
                        "tool_mode": False,
                        "types": ["Message"],
                        "value": "__UNDEFINED__",
                    }
                ],
                "pinned": False,
                "template": template,
                "tool_mode": False,
            },
        },
    }


def langflow(data: dict) -> str:
    by_id = {node["id"]: node for node in data["nodes"]}
    incoming = {node_id: 0 for node_id in by_id}
    for _source, target in data["edges"]:
        incoming[target] += 1
    depth = _depths(data)
    rows: dict[int, int] = {}
    nodes = []
    for node in data["nodes"]:
        column = depth[node["id"]]
        row = rows.get(column, 0)
        rows[column] = row + 1
        position = {"x": 80 + column * 380, "y": 80 + row * 150}
        nodes.append(_langflow_node(node, position, incoming[node["id"]] > 0))

    edges = []
    for source, target in data["edges"]:
        source_handle = _source_handle(by_id[source])
        target_handle = _target_handle(by_id[target])
        edges.append(
            {
                "id": f"reactflow__edge-{source}-{target}",
                "source": source,
                "target": target,
                "sourceHandle": _handle_id(source_handle),
                "targetHandle": _handle_id(target_handle),
                "animated": False,
                "selected": False,
                "className": "",
                "data": {"sourceHandle": source_handle, "targetHandle": target_handle},
            }
        )

    document = {
        "name": data["title"],
        "description": (
            "Generated by scripts/generate_flow.py from docs/flow/simplicio.flow.json. "
            "Conceptual map; not an executable Langflow pipeline."
        ),
        "data": {"nodes": nodes, "edges": edges},
        "is_component": False,
        "endpoint_name": None,
        "flow_type": "workflow",
        "access_type": "PRIVATE",
        "mcp_enabled": False,
        "tags": ["simplicio", "flow-map"],
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def validate_langflow_document(document: object) -> list[str]:
    """Return structural errors for the Langflow import shape (offline check).

    This validates what can be checked without a Langflow server: the FlowCreate
    envelope, the React Flow node wrapper, stable ids and handle wiring. It does
    not prove the UI renders the flow or that the backend accepts the upload.
    """
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["langflow: document must be an object"]
    name = document.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("langflow: name must be a non-empty string")
    if document.get("is_component") is not False:
        errors.append("langflow: is_component must be false")
    if document.get("flow_type") not in {"workflow", "agent"}:
        errors.append("langflow: flow_type must be workflow or agent")
    data = document.get("data")
    if not isinstance(data, dict):
        return errors + ["langflow: data must be an object"]
    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["langflow: data.nodes must be a non-empty list"]
    if not isinstance(edges, list):
        return errors + ["langflow: data.edges must be a list"]

    by_id: dict[str, dict] = {}
    for index, node in enumerate(nodes):
        prefix = f"langflow: node[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(f"{prefix} needs a non-empty id")
            continue
        if node_id in by_id:
            errors.append(f"{prefix} duplicates id {node_id}")
        by_id[node_id] = node
        if node.get("type") != "genericNode":
            errors.append(f"{prefix} type must be genericNode")
        position = node.get("position")
        if not isinstance(position, dict) or not all(isinstance(position.get(axis), int) for axis in ("x", "y")):
            errors.append(f"{prefix} position must carry integer x/y")
        payload = node.get("data")
        if not isinstance(payload, dict):
            errors.append(f"{prefix} data must be an object")
            continue
        if payload.get("id") != node_id:
            errors.append(f"{prefix} data.id must match the wrapper id")
        component = payload.get("type")
        if component not in LANGFLOW_COMPONENT.values():
            errors.append(f"{prefix} data.type must be a Simplicio component")
        definition = payload.get("node")
        if not isinstance(definition, dict):
            errors.append(f"{prefix} data.node must be an object")
            continue
        if not isinstance(definition.get("display_name"), str) or not definition["display_name"]:
            errors.append(f"{prefix} needs a display_name")
        if not isinstance(definition.get("template"), dict):
            errors.append(f"{prefix} template must be an object")
        if not isinstance(definition.get("field_order"), list):
            errors.append(f"{prefix} field_order must be a list")
        elif isinstance(definition.get("template"), dict) and any(
            field not in definition["template"] for field in definition["field_order"]
        ):
            errors.append(f"{prefix} field_order references unknown template fields")
        outputs = definition.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"{prefix} needs at least one output")
        else:
            names = [output.get("name") for output in outputs if isinstance(output, dict)]
            if "output" not in names:
                errors.append(f"{prefix} needs an output named output")

    for index, edge in enumerate(edges):
        prefix = f"langflow: edge[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source = edge.get("source")
        target = edge.get("target")
        if source not in by_id or target not in by_id:
            errors.append(f"{prefix} references an unknown node")
            continue
        if source == target:
            errors.append(f"{prefix} must not be a self edge")
        source_node = by_id[source]
        target_node = by_id[target]
        source_payload = source_node.get("data")
        target_payload = target_node.get("data")
        if not isinstance(source_payload, dict) or not isinstance(target_payload, dict):
            errors.append(f"{prefix} endpoints must carry node data")
            continue
        try:
            source_handle = _source_handle({"id": source, "kind": _kind_for_component(source_payload.get("type"))})
            target_handle = _target_handle({"id": target, "kind": _kind_for_component(target_payload.get("type"))})
        except KeyError:
            errors.append(f"{prefix} endpoints must use Simplicio component types")
            continue
        if edge.get("sourceHandle") != _handle_id(source_handle):
            errors.append(f"{prefix} sourceHandle does not match the source output")
        if edge.get("targetHandle") != _handle_id(target_handle):
            errors.append(f"{prefix} targetHandle does not match the target input")
        handle_data = edge.get("data")
        if (
            not isinstance(handle_data, dict)
            or handle_data.get("sourceHandle") != source_handle
            or handle_data.get("targetHandle") != target_handle
        ):
            errors.append(f"{prefix} data handles must mirror the scaped handles")
        target_definition = target_payload.get("node")
        if not isinstance(target_definition, dict) or "input" not in (target_definition.get("template") or {}):
            errors.append(f"{prefix} target node has no input field for the target handle")

    if _has_volatile_keys(document):
        errors.append("langflow: document must not carry volatile keys")
    return errors


def _kind_for_component(component: object) -> str:
    for kind, value in LANGFLOW_COMPONENT.items():
        if component == value:
            return kind
    raise KeyError(component)


def _has_volatile_keys(value: object) -> bool:
    if isinstance(value, dict):
        return any(key in VOLATILE_KEYS or _has_volatile_keys(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_has_volatile_keys(child) for child in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    data = load()
    outputs = {
        OUT / "simplicio.mmd": mermaid(data),
        OUT / "simplicio.svg": svg(data),
        OUT / "langflow" / "simplicio.langflow.json": langflow(data),
    }
    problems = []
    for path, body in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != body:
                problems.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8", newline="\n")
    if problems:
        print("flow drift: " + ", ".join(problems))
        return 1
    print("flow artifacts generated" if not args.check else "flow artifacts up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
