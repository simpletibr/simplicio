# Flow artifacts

The whole Simplicio flow (input → steps → outputs) is published from a single
source of truth plus three generated artifacts:

| Artifact | Purpose |
|:---|:---|
| `docs/flow/simplicio.flow.json` | Source of truth (`simplicio.flow/v1`) |
| `docs/flow/simplicio.mmd` | Mermaid `flowchart LR` for docs/PRs |
| `docs/flow/simplicio.svg` | Deterministic SVG embedded in the root README |
| `docs/flow/langflow/simplicio.langflow.json` | Langflow import document (conceptual canvas) |

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

## Mermaid CLI (`mmdc`)

`mmdc` is optional: the committed SVG comes from the deterministic generator,
not from Mermaid CLI, so Python-only environments can still regenerate it.

Requirements: Node.js 18+ and `@mermaid-js/mermaid-cli` (which pulls a headless
Chromium via Puppeteer).

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i docs/flow/simplicio.mmd -o /tmp/simplicio.mmd.svg
```

**Status in this environment (2026-10-23): BLOCKED.** `mmdc` is not installed
and a fallback `npx @mermaid-js/mermaid-cli` run did not finish within the local
timeout (Chromium download), so the Mermaid CLI render was not executed. The
committed `simplicio.svg` is the generator output; re-run `mmdc` on a
workstation/CI image with Node and Chromium before claiming CLI validation.

## Langflow

Requirements: Langflow 1.12 reachable at `http://localhost:7860`.

```bash
python3 scripts/verify_flow_langflow.py                 # default endpoint
python3 scripts/verify_flow_langflow.py --base-url http://localhost:7860 --timeout 20
python3 scripts/verify_flow_langflow.py --cleanup       # delete after verified read-back
```

Authentication is read from `LANGFLOW_API_KEY` when present. The API key is
never written to the receipt, logs or docs.

The verifier is fail-closed:

| Exit | Status | Meaning |
|:---:|:---|:---|
| 0 | `verified` | Imported, fetched back, nodes/edges/labels match |
| 1 | `failed` | Import rejected or read-back mismatch |
| 2 | `blocked` | No usable Langflow, no auth, or no import endpoint |

It always prints one machine-readable JSON receipt
(`schema: simplicio.langflow-receipt/v1`) containing the endpoint host/port,
artifact SHA-256, node/edge counts and the boolean checks. It never stores
credentials.

**Status in this environment: BLOCKED.** No Langflow server answered
`http://localhost:7860/api/v1/flows/`, so the flow was **not** imported and no
live import is claimed. The offline contract test only proves the document
matches the Langflow 1.x export envelope (`name`, `data.nodes`, `data.edges`,
`is_component`), the `genericNode` wrapper, stable ids and scaped handle wiring.
It does not prove UI rendering or execution.

Offline checks in `tests/test_flow_contract.py`:

- the envelope matches Langflow's `FlowCreate` requirements (`name`, `data.nodes`, `data.edges`);
- every node is a `genericNode` wrapper whose `data.id` matches the wrapper id;
- every edge handle uses Langflow's `scapedJSONStringfy` ordering (sorted keys, `œ` marker), so React Flow can resolve the handles;
- no `updated_at`, `date_created`, `last_tested_version` or `version_token` is emitted.

Not checked offline: the component registry, UI rendering, execution, or backend acceptance of the upload.

The canvas is a conceptual map: `data.type` uses `SimplicioInput`,
`SimplicioStep` and `SimplicioOutput` placeholders. It is meant to show the
whole flow in Langflow, not to run it as an executable pipeline.
