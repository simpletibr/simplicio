import { describe, expect, it } from "vitest";
import aiBomSchema from "./schemas/desktop-ai-bom-v1.schema.json";
import {
  AI_BOM_SCHEMA,
  EVENT_SCHEMA,
  EVENTS_PAGE_SCHEMA,
  MAX_CURSOR,
  aiBomToJson,
  buildAiBom,
  createReplay,
  parseEventPage,
  type DesktopEventPage,
} from "./activity_replay";
import {
  AI_BOM_SCHEMA_DOCUMENT,
  AI_BOM_MAX_ITEMS,
  asAiBom,
  validateAiBom,
  validateAiBomJson,
} from "./ai_bom_validation";

function recordedPage(): DesktopEventPage {
  const envelope = (overrides: Record<string, unknown>) => ({
    schema: EVENT_SCHEMA,
    event: "run.progress",
    cursor: 1,
    payload: { run_id: "run-432", message: "map: 12 arquivos" },
    ...overrides,
  });
  return parseEventPage({
    schema: EVENTS_PAGE_SCHEMA,
    stream_id: "stream-432",
    events: [
      envelope({ cursor: 1, event: "run.started", payload: { run_id: "run-432", issue: "432", command: "map" } }),
      envelope({ cursor: 2 }),
      envelope({
        cursor: 3,
        event: "plugin.installed",
        payload: { plugin_id: "simplicio-loop", version: "1.2.0" },
      }),
      envelope({
        cursor: 4,
        event: "run.finished",
        payload: { run_id: "run-432", status: "ok", duration_ms: 1200, receipt_id: "receipt-1" },
      }),
    ],
    next_cursor: 4,
    has_more: false,
    head_cursor: 4,
    retention_window: 4096,
  });
}

function exportedBom() {
  return buildAiBom(createReplay(recordedPage(), "2026-10-23T12:00:00.000Z"), {
    source: "runtime",
    generatedAt: "2026-10-23T12:00:00.000Z",
  });
}

type SchemaNode = {
  $id?: string;
  $ref?: string;
  type?: string;
  const?: unknown;
  enum?: unknown[];
  required?: string[];
  maxItems?: number;
  properties?: Record<string, SchemaNode>;
  items?: SchemaNode;
  oneOf?: SchemaNode[];
  $defs?: Record<string, SchemaNode>;
};

const schema = aiBomSchema as unknown as SchemaNode;

function resolve(node: SchemaNode | undefined): SchemaNode | undefined {
  if (!node) return undefined;
  if (node.$ref) return schema.$defs?.[node.$ref.split("/").pop() ?? ""] ?? node;
  return node;
}

function branchFor(node: SchemaNode, instance: unknown): SchemaNode {
  const resolved = resolve(node) ?? {};
  if (resolved.oneOf) {
    const wanted = instance === null ? "null" : Array.isArray(instance) ? "array" : typeof instance;
    const match = resolved.oneOf.map(resolve).find((item) => item?.type === wanted);
    return match ?? resolve(resolved.oneOf[0]) ?? {};
  }
  return resolved;
}

/** Every `required` key the schema declares for an object that the export actually contains. */
function requiredKeys(node: SchemaNode, instance: unknown, path: string[] = []): Array<{ path: string[]; key: string }> {
  const found: Array<{ path: string[]; key: string }> = [];
  if (Array.isArray(instance)) {
    instance.forEach((item, index) => {
      found.push(...requiredKeys(branchFor(node.items ?? {}, item).items ?? node.items ?? {}, item, [...path, String(index)]));
    });
    return found;
  }
  if (!instance || typeof instance !== "object") return found;
  const object = branchFor(node, instance);
  if (!object.properties) return found;
  for (const key of object.required ?? []) found.push({ path, key });
  for (const key of Object.keys(instance)) {
    const child = object.properties[key];
    if (!child) continue;
    found.push(...requiredKeys(child, (instance as Record<string, unknown>)[key], [...path, key]));
  }
  return found;
}

function withoutKey(document: unknown, path: string[], key: string): unknown {
  const clone = JSON.parse(JSON.stringify(document));
  let cursor: any = clone;
  for (const segment of path) cursor = cursor[segment];
  delete cursor[key];
  return clone;
}

describe("AI-BOM export validates against its schema", () => {
  it("publishes a versioned schema document for the export", () => {
    expect(schema.$id).toContain(AI_BOM_SCHEMA_DOCUMENT.replace("schemas/", ""));
    expect(schema.properties?.schema?.const).toBe(AI_BOM_SCHEMA);
    expect(schema.properties?.provenance?.properties?.producer?.const).toBe("simplicio-desktop");
    expect(schema.properties?.runs?.maxItems).toBe(AI_BOM_MAX_ITEMS);
  });

  it("accepts the document that buildAiBom produces", () => {
    const bom = exportedBom();
    const validation = validateAiBom(bom);
    expect(validation.errors).toEqual([]);
    expect(validation.ok).toBe(true);
    expect(asAiBom(bom)).not.toBeNull();
  });

  it("accepts the JSON download and rejects malformed JSON", () => {
    expect(validateAiBomJson(aiBomToJson(exportedBom())).ok).toBe(true);
    expect(validateAiBomJson("{not json").errors).toEqual(["#: invalid_json"]);
  });

  it("rejects a document that is missing any key the schema requires", () => {
    const bom = exportedBom();
    const required = requiredKeys(schema, bom);
    // Root + provenance + redaction + summary + run + six step fields.
    // 6 root + 12 provenance + 6 redaction + 5 summary + 2 runs x 9 + 4 steps x 6.
    expect(required.length).toBe(6 + 12 + 6 + 5 + 2 * 9 + 4 * 6);
    for (const { path, key } of required) {
      const validation = validateAiBom(withoutKey(bom, path, key));
      expect(validation.ok, `${path.join("/")}/${key} should be required`).toBe(false);
      expect(validation.errors.join(" ")).toContain(`${["#", ...path].join("/")}/${key}`);
    }
  });

  it("rejects a value that violates any const or enum the schema declares", () => {
    const cases: Array<[string, unknown]> = [
      ["schema", "simplicio.activity-export/v1"],
      ["source", "demo"],
      ["generatedAt", "2026-10-23 12:00:00"],
      ["provenance.source", "demo"],
      ["provenance.eventSchema", "simplicio.desktop-event/v1"],
      ["provenance.redaction.schema", "simplicio.redaction/v2"],
      ["provenance.redaction.prompts", false],
      ["provenance.redaction.paths", false],
      ["provenance.redaction.unknownFields", "kept"],
      ["provenance.eventCount", 1.5],
      ["provenance.firstCursor", MAX_CURSOR + 1],
      ["summary.runs", -1],
      ["runs.0.source", "daemon"],
      ["runs.0.state", "succeeded"],
      ["runs.0.durationMs", -5],
      ["runs.0.steps.0.kind", "run.invented"],
      ["runs.0.steps.0.cursor", -1],
      ["runs.0.steps.0.status", ""],
    ];
    for (const [path, value] of cases) {
      const clone: any = JSON.parse(JSON.stringify(exportedBom()));
      const segments = path.split(".");
      let cursor = clone;
      for (const segment of segments.slice(0, -1)) cursor = cursor[segment];
      cursor[segments[segments.length - 1]] = value;
      expect(validateAiBom(clone).ok, `${path} = ${JSON.stringify(value)}`).toBe(false);
    }
  });

  it("rejects unknown properties instead of exporting them", () => {
    const bom: any = exportedBom();
    bom.leakedPrompt = "hello";
    bom.provenance.credentials = "token";
    bom.runs[0].steps[0].prompt = "hello";
    const errors = validateAiBom(bom).errors.join(" ");
    expect(errors).toContain("#/leakedPrompt: unknown_property");
    expect(errors).toContain("#/provenance/credentials: unknown_property");
    expect(errors).toContain("#/runs/0/steps/0/prompt: unknown_property");
  });

  it("bounds the runs array and the text fields", () => {
    const tooMany: any = exportedBom();
    tooMany.runs = Array.from({ length: AI_BOM_MAX_ITEMS + 1 }, () => tooMany.runs[0]);
    expect(validateAiBom(tooMany).errors).toContain("#/runs: too_many_items");

    const tooLong: any = exportedBom();
    tooLong.runs[0].steps[0].detail = "x".repeat(4_097);
    expect(validateAiBom(tooLong).errors).toContain("#/runs/0/steps/0/detail: too_long");

    const control: any = exportedBom();
    control.runs[0].status = "ok\u0000";
    expect(validateAiBom(control).errors).toContain("#/runs/0/status: control_character");
  });

  it("rejects a non-object document without throwing", () => {
    for (const value of [null, [], "bom", 42, true]) {
      expect(validateAiBom(value)).toEqual({ ok: false, errors: ["#: expected_object"] });
    }
  });
});
