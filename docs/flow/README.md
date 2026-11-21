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

The current graph has 42 nodes (8 inputs, 27 steps, 7 outputs) and 63 edges.
It covers every public CLI command and every MCP tool documented in
`README.md` and `MCP-CONNECT.md` (13 MCP tools); see [Coverage](#coverage) for the gate that
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

Measured on 2026-11-21 with `PYTHONHASHSEED=0` and `PYTHONHASHSEED=424242`
(both runs byte-identical, and identical to the committed artifacts; the source
file is not written by `--out-dir`, so its hash is that of the committed file):

```
7b64ca9a2f3b4125f0a11447a17460f5cd0fd6c0132c3d38bcf402420d60738f  simplicio.flow.json
b50b315fffd99fef4ab54fd20622c2843de6e4d2cdf74499b02174d55f63e342  simplicio.mmd
72c850ae8955c9baf0244a4433031e8957072752b5ddc7962a1596b3cb9b78d8  simplicio.svg
73cedd7631b50929fcc35b232cccfce29c11c5343f849afe2e9aed7bf3efd7ac  langflow/simplicio.langflow.json
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

The release publisher's `update_flow_version` (`scripts/publish_release_local.py`) writes the release version into the source and regenerates the three generated files, and `scripts/verify_distribution_consistency.py` reports an ERROR when the flow version differs from the manifest version.

## Mermaid CLI (`mmdc`)

The committed `simplicio.svg` comes from the deterministic generator, not from
Mermaid CLI, so Python-only environments can still regenerate it. `mmdc` is
used as an independent render check and for the PNG evidence:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/flow/simplicio.mmd \
  -o docs/flow/render/simplicio.mermaid.png -s 2
```

**Status in this environment: VERIFIED.** Measured 2026-11-21 with
`@mermaid-js/mermaid-cli` 12.0.0 on Node v22.23.5, using the system Chromium
(`/opt/pw-browsers/chromium`, Google Chrome for Testing 153.0.8010.12) through a
Puppeteer config of `{"executablePath": "/opt/pw-browsers/chromium", "args":
["--no-sandbox", "--headless"]}` (`PUPPETEER_SKIP_DOWNLOAD=1`, no browser
download):

```
PUPPETEER_SKIP_DOWNLOAD=1 npx -y @mermaid-js/mermaid-cli@12.0.0 -i docs/flow/simplicio.mmd \
  -o docs/flow/render/simplicio.mermaid.png -s 2 -p puppeteer.json
Generating single mermaid chart
exit=0
docs/flow/render/simplicio.mermaid.png  1568x636
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

**Status in this environment: VERIFIED.** Measured 2026-11-21 against a local
Langflow 1.12.0 server (isolated `python3.12` venv, `LANGFLOW_AUTO_LOGIN=true`,
`LANGFLOW_DO_NOT_TRACK=true`, `langflow run --backend-only`, port 7861; the
server rejected the unauthenticated run with `langflow_auth_required`, so the
verifier ran with a key issued by that local server and passed through
`LANGFLOW_API_KEY`) on the current 42-node artifact, SHA-256
`73cedd7631b50929fcc35b232cccfce29c11c5343f849afe2e9aed7bf3efd7ac`:

```
import_http_status=201  fetch_http_status=200
expected_nodes=42       imported_nodes=42   node_ids_match=true
expected_edges=63       imported_edges=63   edge_pairs_match=true
node_labels_match=true  cleaned_up=true
status=verified         flow_id=a10a5b5f-57ac-4f64-83a1-8a640111fda2
```

Receipt: `docs/flow/evidence/langflow-verify.json` (`flow_id`
`a10a5b5f-57ac-4f64-83a1-8a640111fda2`, removed afterwards by `--cleanup`).
`GET /api/v1/flows/{id}` summary (42 nodes, 63 edges, name, ids and edge pairs,
plus the SHA-256 of the raw response): `docs/flow/evidence/langflow-readback.json`,
captured from a separate import of the same artifact
(`flow_id=504fcac8-6b47-436c-ae38-32faf514249a`, HTTP 200, 86666 bytes; its nodes
and edges equal the artifact's in order, and the flow was deleted afterwards).
The 2026-10-23 receipts that described the earlier 39-node, 53-edge artifact
were replaced by these.

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
