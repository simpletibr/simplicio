#!/usr/bin/env python3
"""Generate Mermaid/SVG/Langflow artifacts from docs/flow/simplicio.flow.json.

The JSON is the single source of truth. Generation is deterministic: the same
input bytes produce the same output bytes. Every non-artifact source must exist
in the repository; drift fails before writing anything.
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


def load() -> dict:
    data = json.loads(FLOW.read_text(encoding="utf-8"))
    if data.get("schema") != "simplicio.flow/v1":
        raise SystemExit("flow: unsupported schema")
    nodes = data.get("nodes", [])
    ids = [node.get("id") for node in nodes]
    if not ids or len(ids) != len(set(ids)):
        raise SystemExit("flow: node ids must be unique and non-empty")
    for node in nodes:
        if node.get("kind") not in KINDS:
            raise SystemExit(f"flow: invalid node kind {node.get('kind')!r}")
        source = node.get("source")
        if source and not (ROOT / source).exists():
            raise SystemExit(f"flow: missing source {source}")
    known = set(ids)
    for edge in data.get("edges", []):
        if len(edge) != 2 or edge[0] not in known or edge[1] not in known:
            raise SystemExit(f"flow: invalid edge {edge!r}")
    return data


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
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#555"/></marker></defs>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="40" y="40" font-family="sans-serif" font-size="20" font-weight="700">{html.escape(data["title"])}</text>',
    ]
    for source, target in data["edges"]:
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        parts.append(f'<line x1="{x1 + 320}" y1="{y1 + 35}" x2="{x2}" y2="{y2 + 35}" stroke="#555" stroke-width="1.5" marker-end="url(#arrow)"/>')
    for node in data["nodes"]:
        x, y = positions[node["id"]]
        kind = node["kind"]
        parts.append(
            f'<rect x="{x}" y="{y}" width="320" height="70" rx="10" fill="{COLORS[kind]}" stroke="{STROKES[kind]}" stroke-width="1.5"/>'
        )
        parts.append(f'<text x="{x + 14}" y="{y + 28}" font-family="sans-serif" font-size="14" font-weight="700">{html.escape(node["id"])}</text>')
        parts.append(f'<text x="{x + 14}" y="{y + 50}" font-family="sans-serif" font-size="12" fill="#333">{html.escape(node["label"])}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def langflow(data: dict) -> str:
    nodes = []
    for index, node in enumerate(data["nodes"]):
        nodes.append({
            "id": node["id"],
            "type": "genericNode",
            "position": {"x": 80 + (index % 4) * 300, "y": 80 + (index // 4) * 220},
            "data": {
                "id": node["id"],
                "type": "genericNode",
                "node": {
                    "display_name": node["label"],
                    "description": f"{node['kind']} · {node.get('source') or node.get('artifact') or ''}",
                    "template": {},
                },
            },
        })
    edges = []
    for source, target in data["edges"]:
        edges.append({
            "id": f"e-{source}-{target}",
            "source": source,
            "target": target,
            "sourceHandle": "output",
            "targetHandle": "input",
            "data": {"sourceHandle": {"name": "output"}, "targetHandle": {"fieldName": "input"}},
        })
    document = {
        "name": data["title"],
        "description": "Generated by scripts/generate_flow.py from simplicio.flow.json",
        "data": {"nodes": nodes, "edges": edges},
        "is_component": False,
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


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
