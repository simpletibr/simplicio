# Flow artifacts

The whole Simplicio flow (inputs → steps → outputs) is published from a single
source of truth plus three generated artifacts:

| Artifact | Purpose |
|:---|:---|
| `docs/flow/simplicio.flow.json` | Source of truth (`simplicio.flow/v1`) |
| `docs/flow/simplicio.mmd` | Mermaid `flowchart LR` for docs/PRs |
| `docs/flow/simplicio.svg` | Deterministic SVG embedded in the root README |
| `docs/flow/langflow/simplicio.langflow.json` | Langflow import document (conceptual canvas) |
| `docs/flow/render/simplicio.mermaid.png` | `mmdc` render evidence |
| `docs/flow/render/RENDER-STATUS.json` | Renderer, command and hashes for that evidence |
| `docs/flow/evidence/langflow-verify.json` | Fail-closed Langflow import receipt |
| `docs/flow/evidence/langflow-readback.json` | Summary of `GET /api/v1/flows/{id}` |

The current graph has 39 nodes (8 inputs, 24 steps, 7 outputs) and 53 edges.
It covers every public CLI command and every MCP tool documented in
`README.md` and `MCP-CONNECT.md`; see [Coverage](#coverage) for the gate that
enforces it.

## Regenerate

```bash
python3 scripts/generate_flow.py
python3 scripts/generate_flow.py --check   # drift gate, writes nothing
```

Generation is deterministic and offline: identical source bytes produce
identical output bytes, with no timestamps, random ids or host paths. Every
`source`/`artifact` referenced by the flow must exist before anything is
written. Node ids are stable; Langflow edge ids are `reactflow__edge-<source>-<target>`
and edge handles are derived from the node ids.

`--out-dir` writes the same artifacts somewhere else without touching the
committed files. The contract test uses it to generate twice, in different
directories and with different `PYTHONHASHSEED` values, then compares SHA-256
against the committed bytes:

```bash
python3 scripts/generate_flow.py --out-dir /tmp/flow-a
python3 scripts/generate_flow.py --out-dir /tmp/flow-b
shasum -a 256 /tmp/flow-a/* /tmp/flow-b/*
```

Measured on 2026-10-23 (both runs byte-identical, and identical to the
committed artifacts):

```
8668129935dd23928fad224bdeae863678be33e888e8c9647a54441e3479a854  simplicio.flow.json
6abdc271987201578700be1c483f043ed02bea9bbab0ffa51e06535b80d769f2  simplicio.mmd
fd69eabba0271a514aaf57a3b16ada457ef281a7809dcfefd0133ce0f45d1eaa  simplicio.svg
897954600e6b88051fc9a5fb9ebb338c823519239e05d16302c2bce818948fb5  langflow/simplicio.langflow.json
```

## Coverage

`tests/test_flow_contract.py` fails when the flow drifts from the public
surface:

- every `simplicio <command>` mentioned in `README.md` or `MCP-CONNECT.md` must
  be a node of the flow, and the flow may not cite a command those docs do not
  declare;
- every MCP tool listed in `MCP-CONNECT.md` must be a node, and the flow may not
  invent a tool;
- `simplicio` commands must resolve to the `bin` entry of
  `npm/simplicio/package.json` and the `[project.scripts]` entry of
  `pypi/simplicio/pyproject.toml`;
- `python3 scripts/...` commands must point at a file that exists;
- every step must be reachable from an input and must reach an output;
- `version` must match `version.txt`.

## Mermaid CLI (`mmdc`)

The committed `simplicio.svg` comes from the deterministic generator, not from
Mermaid CLI, so Python-only environments can still regenerate it. `mmdc` is
used as an independent render check and for the PNG evidence:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/flow/simplicio.mmd \
  -o docs/flow/render/simplicio.mermaid.png -s 2
```

**Status in this environment: VERIFIED.** Measured 2026-10-23 with
`@mermaid-js/mermaid-cli` 12.0.0 on Node v26.8.2:

```
Generating single mermaid chart
exit=0
docs/flow/render/simplicio.mermaid.png  1568x606
```

The renderer, exact command, input hash and output hash live in
`docs/flow/render/RENDER-STATUS.json`. The contract test fails if the `.mmd`
changes without re-rendering that evidence. `mmdc` output is not byte-stable
across machines, so it is never used as the committed diagram.

## Langflow

Requirements: Langflow 1.12 reachable at `http://localhost:7860`.

```bash
python3 scripts/verify_flow_langflow.py                 # default endpoint
python3 scripts/verify_flow_langflow.py --base-url http://localhost:7860 --timeout 20
python3 scripts/verify_flow_langflow.py --cleanup       # delete after verified read-back
python3 scripts/verify_flow_langflow.py --api-key-file ~/.config/simplicio/langflow.key \
  --evidence docs/flow/evidence/langflow-verify.json
```

Authentication is read from `LANGFLOW_API_KEY`, from `--api-key-file`, or from
`LANGFLOW_API_KEY_FILE` when set. The key is never written to the receipt,
logs or docs.

The verifier is fail-closed:

| Exit | Status | Meaning |
|:---:|:---|:---|
| 0 | `verified` | Imported, fetched back, nodes/edges/labels match |
| 1 | `failed` | Import rejected or read-back mismatch |
| 2 | `blocked` | No usable Langflow, no auth, no import endpoint, or unreadable key file |

It always prints one machine-readable JSON receipt
(`schema: simplicio.langflow-receipt/v1`) containing the endpoint host/port,
artifact SHA-256, node/edge counts and the boolean checks. It never stores
credentials.

**Status in this environment: VERIFIED.** Measured 2026-10-23 against a local
Langflow 1.12.0 server (isolated `python3.12` venv, `LANGFLOW_AUTO_LOGIN=true`,
port 7861):

```
import_http_status=201  fetch_http_status=200
expected_nodes=39       imported_nodes=39   node_ids_match=true
expected_edges=53       imported_edges=53   edge_pairs_match=true
node_labels_match=true  cleaned_up=true
status=verified         flow_id=7c6d9aaf-fc4f-439b-a7db-74f3ee7ec041
```

Receipt: `docs/flow/evidence/langflow-verify.json` (`flow_id`
`7c6d9aaf-fc4f-439b-a7db-74f3ee7ec041`, removed afterwards by `--cleanup`).
`GET /api/v1/flows/{id}` summary (39 nodes, 53 edges, name, ids and edge pairs,
plus the SHA-256 of the raw response): `docs/flow/evidence/langflow-readback.json`,
captured from a separate import of the same artifact
(`flow_id=d43ce742-eab6-4bc0-a0e3-9d9d10971e91`).

The headless check used the API plus the returned JSON, not a GUI screenshot:
the UI needs an authenticated browser session, which this environment does not
provide. The visual evidence is the `mmdc` PNG above, rendered from the same
graph.

Offline checks in `tests/test_flow_contract.py` remain necessary because a live
server is not always available:

- the envelope matches Langflow's `FlowCreate` requirements (`name`, `data.nodes`, `data.edges`);
- every node is a `genericNode` wrapper whose `data.id` matches the wrapper id;
- every edge handle uses Langflow's `scapedJSONStringfy` ordering (sorted keys, `œ` marker), so React Flow can resolve the handles;
- no `updated_at`, `date_created`, `last_tested_version` or `version_token` is emitted.

Not checked offline: the component registry, UI rendering, execution, or backend acceptance of the upload.

The canvas is a conceptual map: `data.type` uses `SimplicioInput`,
`SimplicioStep` and `SimplicioOutput` placeholders. It is meant to show the
whole flow in Langflow, not to run it as an executable pipeline.
