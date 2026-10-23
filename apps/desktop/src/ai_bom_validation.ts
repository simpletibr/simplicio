/**
 * Fail-closed validator for the Desktop AI-BOM export.
 *
 * The contract lives in `src/schemas/desktop-ai-bom-v1.schema.json`; this module
 * is the executable form of it. `buildAiBom` never calls the validator, so a
 * regression in the export cannot hide behind its own check: the tests validate
 * a freshly built document and every constraint the schema declares.
 */
import {
  AI_BOM_SCHEMA,
  EVENT_KINDS,
  MAX_CURSOR,
  REDACTION_SCHEMA,
  type AiBom,
} from "./activity_replay";

export const AI_BOM_SCHEMA_DOCUMENT = "schemas/desktop-ai-bom-v1.schema.json";
export const AI_BOM_MAX_ITEMS = 500;
export const AI_BOM_MAX_TEXT = 512;
// Built from a 1024-code-point message; redaction markers can make it longer.
export const AI_BOM_MAX_DETAIL = 4096;
const MAX_ERRORS = 32;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$/;

export interface AiBomValidation {
  ok: boolean;
  errors: string[];
}

class Checker {
  readonly errors: string[] = [];

  fail(path: string, rule: string): void {
    if (this.errors.length < MAX_ERRORS) this.errors.push(`${path}: ${rule}`);
  }

  object(value: unknown, path: string, keys: readonly string[]): Record<string, unknown> | null {
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      this.fail(path, "expected_object");
      return null;
    }
    const record = value as Record<string, unknown>;
    for (const key of keys) {
      if (!Object.prototype.hasOwnProperty.call(record, key)) this.fail(`${path}/${key}`, "missing_required");
    }
    for (const key of Object.keys(record)) {
      if (!keys.includes(key)) this.fail(`${path}/${key}`, "unknown_property");
    }
    return record;
  }

  array(value: unknown, path: string, max: number): unknown[] | null {
    if (!Array.isArray(value)) {
      this.fail(path, "expected_array");
      return null;
    }
    if (value.length > max) this.fail(path, "too_many_items");
    return value;
  }

  constString(value: unknown, path: string, expected: string): void {
    if (value !== expected) this.fail(path, "expected_const");
  }

  constTrue(value: unknown, path: string): void {
    if (value !== true) this.fail(path, "expected_true");
  }

  text(value: unknown, path: string, max: number): void {
    if (typeof value !== "string") {
      this.fail(path, "expected_string");
      return;
    }
    const length = [...value].length;
    if (length < 1) this.fail(path, "too_short");
    if (length > max) this.fail(path, "too_long");
    if (/[\u0000-\u001f\u007f]/.test(value)) this.fail(path, "control_character");
  }

  nullableText(value: unknown, path: string, max: number): void {
    if (value !== null) this.text(value, path, max);
  }

  count(value: unknown, path: string): void {
    if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) {
      this.fail(path, "expected_non_negative_integer");
    }
  }

  cursor(value: unknown, path: string): void {
    if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0 || value > MAX_CURSOR) {
      this.fail(path, "expected_cursor");
    }
  }

  nullableCursor(value: unknown, path: string): void {
    if (value !== null) this.cursor(value, path);
  }

  nullableDuration(value: unknown, path: string): void {
    if (value === null) return;
    if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) {
      this.fail(path, "expected_nullable_duration");
    }
  }

  enum(value: unknown, path: string, allowed: readonly string[]): void {
    if (typeof value !== "string" || !allowed.includes(value)) this.fail(path, "expected_enum");
  }

  timestamp(value: unknown, path: string): void {
    if (typeof value !== "string" || !TIMESTAMP.test(value)) this.fail(path, "expected_timestamp");
  }
}

function checkRedaction(check: Checker, value: unknown, path: string): void {
  const redaction = check.object(value, path, [
    "schema",
    "prompts",
    "credentials",
    "paths",
    "unknownFields",
    "redactionsApplied",
  ]);
  if (redaction === null) return;
  check.constString(redaction.schema, `${path}/schema`, REDACTION_SCHEMA);
  check.constTrue(redaction.prompts, `${path}/prompts`);
  check.constTrue(redaction.credentials, `${path}/credentials`);
  check.constTrue(redaction.paths, `${path}/paths`);
  check.constString(redaction.unknownFields, `${path}/unknownFields`, "dropped");
  check.count(redaction.redactionsApplied, `${path}/redactionsApplied`);
}

function checkProvenance(check: Checker, value: unknown, path: string): void {
  const provenance = check.object(value, path, [
    "producer",
    "source",
    "eventSchema",
    "streamId",
    "firstCursor",
    "lastCursor",
    "eventCount",
    "rejectedEvents",
    "stepCount",
    "receiptCount",
    "replayGeneratedAt",
    "redaction",
  ]);
  if (provenance === null) return;
  check.constString(provenance.producer, `${path}/producer`, "simplicio-desktop");
  check.enum(provenance.source, `${path}/source`, ["runtime", "preview"]);
  check.constString(provenance.eventSchema, `${path}/eventSchema`, "simplicio.desktop-events/v1");
  check.nullableText(provenance.streamId, `${path}/streamId`, AI_BOM_MAX_TEXT);
  check.nullableCursor(provenance.firstCursor, `${path}/firstCursor`);
  check.nullableCursor(provenance.lastCursor, `${path}/lastCursor`);
  check.count(provenance.eventCount, `${path}/eventCount`);
  check.count(provenance.rejectedEvents, `${path}/rejectedEvents`);
  check.count(provenance.stepCount, `${path}/stepCount`);
  check.count(provenance.receiptCount, `${path}/receiptCount`);
  check.timestamp(provenance.replayGeneratedAt, `${path}/replayGeneratedAt`);
  checkRedaction(check, provenance.redaction, `${path}/redaction`);
}

function checkStep(check: Checker, value: unknown, path: string): void {
  const step = check.object(value, path, ["sequence", "cursor", "kind", "status", "detail", "receiptId"]);
  if (step === null) return;
  check.count(step.sequence, `${path}/sequence`);
  check.cursor(step.cursor, `${path}/cursor`);
  check.enum(step.kind, `${path}/kind`, EVENT_KINDS);
  check.text(step.status, `${path}/status`, AI_BOM_MAX_TEXT);
  check.nullableText(step.detail, `${path}/detail`, AI_BOM_MAX_DETAIL);
  check.nullableText(step.receiptId, `${path}/receiptId`, AI_BOM_MAX_TEXT);
}

function checkRun(check: Checker, value: unknown, path: string): void {
  const run = check.object(value, path, [
    "id",
    "source",
    "worktree",
    "state",
    "status",
    "command",
    "durationMs",
    "receipts",
    "steps",
  ]);
  if (run === null) return;
  check.text(run.id, `${path}/id`, AI_BOM_MAX_TEXT);
  check.enum(run.source, `${path}/source`, ["run", "runtime"]);
  check.nullableText(run.worktree, `${path}/worktree`, AI_BOM_MAX_TEXT);
  check.enum(run.state, `${path}/state`, ["running", "finished", "unknown"]);
  check.text(run.status, `${path}/status`, AI_BOM_MAX_TEXT);
  check.nullableText(run.command, `${path}/command`, AI_BOM_MAX_TEXT);
  check.nullableDuration(run.durationMs, `${path}/durationMs`);
  const receipts = check.array(run.receipts, `${path}/receipts`, AI_BOM_MAX_ITEMS);
  receipts?.forEach((receipt, index) => check.text(receipt, `${path}/receipts/${index}`, AI_BOM_MAX_TEXT));
  const steps = check.array(run.steps, `${path}/steps`, AI_BOM_MAX_ITEMS);
  steps?.forEach((step, index) => checkStep(check, step, `${path}/steps/${index}`));
}

/** Validate one exported document. Empty `errors` means it satisfies the schema. */
export function validateAiBom(value: unknown): AiBomValidation {
  const check = new Checker();
  const bom = check.object(value, "#", ["schema", "generatedAt", "source", "provenance", "summary", "runs"]);
  if (bom !== null) {
    check.constString(bom.schema, "#/schema", AI_BOM_SCHEMA);
    check.timestamp(bom.generatedAt, "#/generatedAt");
    check.enum(bom.source, "#/source", ["runtime", "preview"]);
    checkProvenance(check, bom.provenance, "#/provenance");
    const summary = check.object(bom.summary, "#/summary", ["runs", "finished", "running", "receipts", "redactions"]);
    if (summary !== null) {
      for (const key of ["runs", "finished", "running", "receipts", "redactions"] as const) {
        check.count(summary[key], `#/summary/${key}`);
      }
    }
    const runs = check.array(bom.runs, "#/runs", AI_BOM_MAX_ITEMS);
    runs?.forEach((run, index) => checkRun(check, run, `#/runs/${index}`));
  }
  return { ok: check.errors.length === 0, errors: check.errors };
}

/** Parse the exported JSON string and validate it in one step. */
export function validateAiBomJson(text: string): AiBomValidation {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    return { ok: false, errors: ["#: invalid_json"] };
  }
  return validateAiBom(parsed);
}

/** Narrow a validated document for callers that need the typed shape. */
export function asAiBom(value: unknown): AiBom | null {
  return validateAiBom(value).ok ? (value as AiBom) : null;
}
