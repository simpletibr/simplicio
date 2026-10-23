/**
 * Flight recorder for the Runtime desktop event stream (#432).
 *
 * Contracts (verified against the Runtime schemas):
 * - `simplicio.desktop-events-page/v1` is the page the daemon `events` method
 *   returns; `simplicio.desktop-events/v1` is the envelope of each event.
 * - `simplicio.desktop-event/v1` is accepted as a legacy alias of the envelope
 *   only; the canonical id above is the one written by the Runtime.
 * - `simplicio.activity-replay/v1` is the deterministic projection and
 *   `simplicio.desktop-ai-bom/v1` is the provenance export.
 *
 * Everything here is fail-closed: an event whose envelope, kind, cursor or
 * required payload does not match is rejected instead of being repaired.
 * Optional fields that are absent stay `null`/`unknown`; they are never
 * inferred from neighbouring events.
 */

export const EVENTS_PAGE_SCHEMA = "simplicio.desktop-events-page/v1";
export const EVENT_SCHEMA = "simplicio.desktop-events/v1";
export const EVENT_SCHEMA_ALIASES = ["simplicio.desktop-event/v1"] as const;
export const REPLAY_SCHEMA = "simplicio.activity-replay/v1";
export const AI_BOM_SCHEMA = "simplicio.desktop-ai-bom/v1";
export const REDACTION_SCHEMA = "simplicio.redaction/v1";
export const RUNTIME_RUN_ID = "runtime";

/** The Desktop native bridge serves at most 500 events and 1 MB per page. */
export const MAX_EVENTS = 500;
export const MAX_PAGE_BYTES = 1_000_000;
/** Cursors above this cannot round-trip through a JS number without loss. */
export const MAX_CURSOR = 9_007_199_254_740_991;
export const MAX_TEXT = 512;
export const MAX_MESSAGE = 1_024;

const CONTROL_CHARACTER = /[\u0000-\u001f\u007f]/;
const SCHEMAS: ReadonlySet<string> = new Set([EVENT_SCHEMA, ...EVENT_SCHEMA_ALIASES]);

export type DesktopEventKind =
  | "run.started"
  | "run.progress"
  | "run.finished"
  | "plugin.installed"
  | "plugin.updated"
  | "plugin.removed"
  | "host.connected"
  | "host.disconnected"
  | "map.baseline.building"
  | "map.baseline.ready"
  | "update.available"
  | "update.applied";

export const EVENT_KINDS: readonly DesktopEventKind[] = [
  "run.started",
  "run.progress",
  "run.finished",
  "plugin.installed",
  "plugin.updated",
  "plugin.removed",
  "host.connected",
  "host.disconnected",
  "map.baseline.building",
  "map.baseline.ready",
  "update.available",
  "update.applied",
];

export type ReplayErrorCode =
  | "invalid_envelope"
  | "unsupported_schema"
  | "unknown_event_kind"
  | "invalid_cursor"
  | "invalid_payload"
  | "oversized_event"
  | "invalid_page"
  | "page_too_large"
  | "page_too_many_events";

export class ReplayParseError extends Error {
  readonly code: ReplayErrorCode;

  constructor(code: ReplayErrorCode) {
    super(code);
    this.name = "ReplayParseError";
    this.code = code;
  }
}

export interface DesktopEventPayload {
  runId: string | null;
  issue: string | null;
  command: string | null;
  message: string | null;
  status: string | null;
  durationMs: number | null;
  receiptId: string | null;
  pluginId: string | null;
  version: string | null;
  fromVersion: string | null;
  toVersion: string | null;
  hostId: string | null;
  reason: string | null;
  mapId: string | null;
  nodeCount: number | null;
}

export interface DesktopEvent {
  schema: typeof EVENT_SCHEMA;
  kind: DesktopEventKind;
  cursor: number;
  payload: DesktopEventPayload;
}

export interface DesktopEventPage {
  schema: typeof EVENTS_PAGE_SCHEMA;
  streamId: string;
  events: DesktopEvent[];
  /** Events the page carried but the strict parser refused; never rendered. */
  rejected: number;
  nextCursor: number;
  hasMore: boolean;
  headCursor: number;
  retentionWindow: number;
}

export type ReplayRunSource = "run" | "runtime";
export type ReplayRunState = "running" | "finished" | "unknown";
export type ReplayStepStatus = string;

export interface ReplayStep {
  sequence: number;
  cursor: number;
  kind: DesktopEventKind;
  label: string;
  status: ReplayStepStatus;
  detail: string | null;
  receiptId: string | null;
  redactions: number;
}

export interface ReplayRun {
  id: string;
  source: ReplayRunSource;
  worktree: string | null;
  issue: string | null;
  command: string | null;
  state: ReplayRunState;
  status: ReplayStepStatus;
  durationMs: number | null;
  startedCursor: number | null;
  finishedCursor: number | null;
  steps: ReplayStep[];
  receipts: string[];
}

export interface ReplayReceipt {
  runId: string;
  receiptId: string;
  cursor: number;
}

export interface ActivityReplay {
  schema: typeof REPLAY_SCHEMA;
  generatedAt: string;
  streamId: string | null;
  eventCount: number;
  rejectedEvents: number;
  headCursor: number;
  redactions: number;
  runs: ReplayRun[];
  receipts: ReplayReceipt[];
}

export interface AiBomProvenance {
  producer: "simplicio-desktop";
  source: "runtime" | "preview";
  eventSchema: typeof EVENT_SCHEMA;
  streamId: string | null;
  firstCursor: number | null;
  lastCursor: number | null;
  eventCount: number;
  rejectedEvents: number;
  stepCount: number;
  receiptCount: number;
  replayGeneratedAt: string;
  redaction: {
    schema: typeof REDACTION_SCHEMA;
    prompts: true;
    credentials: true;
    paths: true;
    unknownFields: "dropped";
    redactionsApplied: number;
  };
}

export interface AiBomStep {
  sequence: number;
  cursor: number;
  kind: DesktopEventKind;
  status: ReplayStepStatus;
  detail: string | null;
  receiptId: string | null;
}

export interface AiBomRun {
  id: string;
  source: ReplayRunSource;
  worktree: string | null;
  state: ReplayRunState;
  status: ReplayStepStatus;
  command: string | null;
  durationMs: number | null;
  receipts: string[];
  steps: AiBomStep[];
}

export interface AiBom {
  schema: typeof AI_BOM_SCHEMA;
  generatedAt: string;
  source: "runtime" | "preview";
  provenance: AiBomProvenance;
  summary: {
    runs: number;
    finished: number;
    running: number;
    receipts: number;
    redactions: number;
  };
  runs: AiBomRun[];
}

type JsonRecord = Record<string, unknown>;

function asRecord(value: unknown, code: ReplayErrorCode): JsonRecord {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new ReplayParseError(code);
  }
  return value as JsonRecord;
}

function readText(record: JsonRecord, key: string, max: number, required: boolean): string | null {
  const value = record[key];
  if (value === undefined || value === null) {
    if (required) throw new ReplayParseError("invalid_payload");
    return null;
  }
  if (typeof value !== "string" || value.length > max || CONTROL_CHARACTER.test(value)) {
    throw new ReplayParseError("invalid_payload");
  }
  if (value.length === 0) {
    if (required) throw new ReplayParseError("invalid_payload");
    return null;
  }
  return value;
}

function readInteger(record: JsonRecord, key: string, required: boolean): number | null {
  const value = record[key];
  if (value === undefined || value === null) {
    if (required) throw new ReplayParseError("invalid_payload");
    return null;
  }
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0 || value > MAX_CURSOR) {
    throw new ReplayParseError("invalid_payload");
  }
  return value;
}

function readCursor(value: unknown): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0 || value > MAX_CURSOR) {
    throw new ReplayParseError("invalid_cursor");
  }
  return value;
}

function isEventKind(value: string): value is DesktopEventKind {
  return (EVENT_KINDS as readonly string[]).includes(value);
}

function emptyPayload(): DesktopEventPayload {
  return {
    runId: null,
    issue: null,
    command: null,
    message: null,
    status: null,
    durationMs: null,
    receiptId: null,
    pluginId: null,
    version: null,
    fromVersion: null,
    toVersion: null,
    hostId: null,
    reason: null,
    mapId: null,
    nodeCount: null,
  };
}

function parsePayload(kind: DesktopEventKind, raw: unknown): DesktopEventPayload {
  const record = asRecord(raw, "invalid_payload");
  const payload = emptyPayload();
  // Only the documented keys are copied. Unknown keys are dropped, never
  // forward-declared into the export as if the Runtime had emitted them.
  switch (kind) {
    case "run.started":
      payload.runId = readText(record, "run_id", MAX_TEXT, true);
      payload.issue = readText(record, "issue", MAX_TEXT, false);
      payload.command = readText(record, "command", MAX_TEXT, false);
      break;
    case "run.progress":
      payload.runId = readText(record, "run_id", MAX_TEXT, true);
      payload.message = readText(record, "message", MAX_MESSAGE, true);
      break;
    case "run.finished":
      payload.runId = readText(record, "run_id", MAX_TEXT, true);
      payload.status = readText(record, "status", MAX_TEXT, true);
      payload.durationMs = readInteger(record, "duration_ms", false);
      payload.receiptId = readText(record, "receipt_id", MAX_TEXT, false);
      break;
    case "plugin.installed":
      payload.pluginId = readText(record, "plugin_id", MAX_TEXT, true);
      payload.version = readText(record, "version", MAX_TEXT, true);
      break;
    case "plugin.updated":
      payload.pluginId = readText(record, "plugin_id", MAX_TEXT, true);
      payload.fromVersion = readText(record, "from_version", MAX_TEXT, true);
      payload.toVersion = readText(record, "to_version", MAX_TEXT, true);
      break;
    case "plugin.removed":
      payload.pluginId = readText(record, "plugin_id", MAX_TEXT, true);
      break;
    case "host.connected":
      payload.hostId = readText(record, "host_id", MAX_TEXT, true);
      break;
    case "host.disconnected":
      payload.hostId = readText(record, "host_id", MAX_TEXT, true);
      payload.reason = readText(record, "reason", MAX_TEXT, false);
      break;
    case "map.baseline.building":
      payload.mapId = readText(record, "map_id", MAX_TEXT, true);
      break;
    case "map.baseline.ready":
      payload.mapId = readText(record, "map_id", MAX_TEXT, true);
      payload.nodeCount = readInteger(record, "node_count", false);
      break;
    case "update.available":
    case "update.applied":
      payload.version = readText(record, "version", MAX_TEXT, true);
      break;
    default:
      throw new ReplayParseError("unknown_event_kind");
  }
  return payload;
}

/** Parse one `simplicio.desktop-events/v1` envelope. Throws on any mismatch. */
export function parseDesktopEvent(raw: unknown): DesktopEvent {
  const record = asRecord(raw, "invalid_envelope");
  const schema = record.schema;
  if (typeof schema !== "string" || !SCHEMAS.has(schema)) {
    throw new ReplayParseError("unsupported_schema");
  }
  const kind = readText(record, "event", MAX_TEXT, true);
  if (kind === null || !isEventKind(kind)) {
    throw new ReplayParseError("unknown_event_kind");
  }
  const cursor = readCursor(record.cursor);
  const payload = parsePayload(kind, record.payload);
  const event: DesktopEvent = { schema: EVENT_SCHEMA, kind, cursor, payload };
  if (utf8Bytes(JSON.stringify(event)) > MAX_PAGE_BYTES) {
    throw new ReplayParseError("oversized_event");
  }
  return event;
}

export function tryParseDesktopEvent(raw: unknown): { ok: true; event: DesktopEvent } | { ok: false; code: ReplayErrorCode } {
  try {
    return { ok: true, event: parseDesktopEvent(raw) };
  } catch (error) {
    return { ok: false, code: error instanceof ReplayParseError ? error.code : "invalid_envelope" };
  }
}

/**
 * Parse a `simplicio.desktop-events-page/v1` page. A single malformed event is
 * counted in `rejected` and never reaches the replay; the page itself must be
 * well formed or nothing is returned.
 */
export function parseEventPage(raw: unknown, limit = MAX_EVENTS): DesktopEventPage {
  const record = asRecord(raw, "invalid_page");
  if (record.schema !== EVENTS_PAGE_SCHEMA) throw new ReplayParseError("unsupported_schema");
  const streamId = readText(record, "stream_id", MAX_TEXT, true);
  if (streamId === null) throw new ReplayParseError("invalid_page");
  if (!Array.isArray(record.events)) throw new ReplayParseError("invalid_page");
  if (record.events.length > MAX_EVENTS) throw new ReplayParseError("page_too_many_events");
  const pageBytes = utf8Bytes(JSON.stringify(record));
  if (pageBytes > MAX_PAGE_BYTES) throw new ReplayParseError("page_too_large");

  const events: DesktopEvent[] = [];
  const cap = Math.max(1, Math.min(limit, MAX_EVENTS));
  let rejected = 0;
  let truncated = false;
  for (const candidate of record.events) {
    try {
      const event = parseDesktopEvent(candidate);
      if (events.length >= cap) {
        truncated = true;
        continue;
      }
      events.push(event);
    } catch {
      rejected += 1;
    }
  }

  const declaredNext = readInteger(record, "next_cursor", true);
  const headCursor = readInteger(record, "head_cursor", true);
  const retentionWindow = readInteger(record, "retention_window", true);
  if (declaredNext === null || headCursor === null || retentionWindow === null) {
    throw new ReplayParseError("invalid_page");
  }
  if (typeof record.has_more !== "boolean") throw new ReplayParseError("invalid_page");
  const hasMore = record.has_more || truncated;

  return {
    schema: EVENTS_PAGE_SCHEMA,
    streamId,
    events: orderEvents(events),
    rejected,
    nextCursor: truncated && events.length > 0 ? events[events.length - 1].cursor : declaredNext,
    hasMore,
    headCursor,
    retentionWindow,
  };
}

/** Stable JSON form used for deterministic duplicate tie-breaks. */
function canonical(value: unknown): string {
  if (value === null || value === undefined) return "null";
  if (typeof value !== "object") return JSON.stringify(value) ?? "null";
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  const record = value as JsonRecord;
  return `{${Object.keys(record)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${canonical(record[key])}`)
    .join(",")}}`;
}

/**
 * Cursor order with duplicate cursors collapsed. When two different events
 * claim the same cursor the lexicographically smallest canonical form wins, so
 * the outcome does not depend on arrival order.
 */
export function orderEvents(events: readonly DesktopEvent[]): DesktopEvent[] {
  const byCursor = new Map<number, { event: DesktopEvent; key: string }>();
  for (const event of events) {
    const key = canonical(event);
    const existing = byCursor.get(event.cursor);
    if (!existing || key < existing.key) byCursor.set(event.cursor, { event, key });
  }
  return [...byCursor.values()]
    .sort((left, right) => left.event.cursor - right.event.cursor)
    .map((entry) => entry.event);
}

/** Append a newer page to the retained replay window without duplicating cursors. */
export function mergeEventPages(previous: DesktopEventPage | null, next: DesktopEventPage): DesktopEventPage {
  if (!previous) {
    return { ...next, events: orderEvents(next.events).slice(-MAX_EVENTS) };
  }
  const merged = orderEvents([...previous.events, ...next.events]);
  const kept = merged.slice(-MAX_EVENTS);
  return {
    schema: EVENTS_PAGE_SCHEMA,
    streamId: next.streamId,
    events: kept,
    rejected: previous.rejected + next.rejected,
    nextCursor: Math.max(previous.nextCursor, next.nextCursor, kept.length > 0 ? kept[kept.length - 1].cursor : 0),
    hasMore: next.hasMore,
    headCursor: Math.max(previous.headCursor, next.headCursor),
    retentionWindow: next.retentionWindow,
  };
}

export interface RedactionResult {
  text: string;
  redactions: number;
}

const REDACTIONS: Array<{ pattern: RegExp; replacement: string }> = [
  { pattern: /\b(?:sk|pk|rk)-[A-Za-z0-9_-]{8,}\b/g, replacement: "[redacted-secret]" },
  { pattern: /\bgh[pousr]_[A-Za-z0-9]{8,}\b/g, replacement: "[redacted-secret]" },
  { pattern: /\bxox[baprs]-[A-Za-z0-9-]{8,}\b/g, replacement: "[redacted-secret]" },
  { pattern: /\bBearer\s+[A-Za-z0-9._~+/=-]{8,}/gi, replacement: "Bearer [redacted-secret]" },
  { pattern: /\b(api[_-]?key|token|secret|password)\s*[=:]\s*[^\s,;]+/gi, replacement: "$1=[redacted-secret]" },
  { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, replacement: "[redacted-email]" },
  { pattern: /(?:[A-Za-z]:\\[^\s"'<>|]+|\/(?:Users|home)\/[^\s"'<>|]+)/g, replacement: "[redacted-path]" },
];

/** Redact secret-shaped substrings; the count is provenance, not a metric. */
export function redactText(value: string): RedactionResult {
  let text = value;
  let redactions = 0;
  for (const { pattern, replacement } of REDACTIONS) {
    text = text.replace(pattern, (...args: unknown[]) => {
      redactions += 1;
      const groups = args.slice(1, -2) as Array<string | undefined>;
      return replacement.replace("$1", groups[0] ?? "");
    });
  }
  return { text, redactions };
}

function stepDetail(event: DesktopEvent): { label: string; detail: string | null } {
  const payload = event.payload;
  switch (event.kind) {
    case "run.started":
      return { label: payload.command ? `Início · ${payload.command}` : "Início da execução", detail: payload.issue };
    case "run.progress":
      return { label: "Progresso", detail: payload.message };
    case "run.finished":
      return {
        label: "Fim da execução",
        detail: payload.durationMs === null ? payload.status : `${payload.status} · ${payload.durationMs} ms`,
      };
    case "plugin.installed":
      return { label: "Plugin instalado", detail: [payload.pluginId, payload.version].filter(Boolean).join(" ") || null };
    case "plugin.updated":
      return { label: "Plugin atualizado", detail: [payload.pluginId, payload.fromVersion, "→", payload.toVersion].filter(Boolean).join(" ") || null };
    case "plugin.removed":
      return { label: "Plugin removido", detail: payload.pluginId };
    case "host.connected":
      return { label: "Host conectado", detail: payload.hostId };
    case "host.disconnected":
      return { label: "Host desconectado", detail: [payload.hostId, payload.reason].filter(Boolean).join(" · ") || null };
    case "map.baseline.building":
      return { label: "Mapa: baseline em construção", detail: payload.mapId };
    case "map.baseline.ready":
      return { label: "Mapa: baseline pronta", detail: [payload.mapId, payload.nodeCount === null ? null : `${payload.nodeCount} nós`].filter(Boolean).join(" · ") || null };
    case "update.available":
      return { label: "Atualização disponível", detail: payload.version };
    case "update.applied":
      return { label: "Atualização aplicada", detail: payload.version };
    default:
      return { label: "Evento", detail: null };
  }
}

function createStep(event: DesktopEvent, sequence: number): ReplayStep {
  const described = stepDetail(event);
  const label = redactText(described.label);
  const detail = described.detail === null ? null : redactText(described.detail);
  return {
    sequence,
    cursor: event.cursor,
    kind: event.kind,
    label: label.text,
    // Only `run.finished` carries a status. Anything else is explicitly
    // unknown instead of being inferred as success.
    status: event.kind === "run.finished" ? event.payload.status ?? "unknown" : "unknown",
    detail: detail === null ? null : detail.text,
    receiptId: event.kind === "run.finished" ? event.payload.receiptId : null,
    redactions: label.redactions + (detail?.redactions ?? 0),
  };
}

/**
 * Reconstruct ordered steps per run/worktree. Non-run lifecycle events are
 * grouped under the explicit `runtime` bucket; they are never attached to a run
 * they did not name.
 */
export function createReplay(page: Pick<DesktopEventPage, "events" | "streamId" | "headCursor"> & { rejected?: number }, generatedAt = new Date().toISOString()): ActivityReplay {
  const events = orderEvents(page.events);
  const runs = new Map<string, ReplayRun>();
  const receipts: ReplayReceipt[] = [];
  let redactions = 0;

  for (const event of events) {
    const runId = event.payload.runId ?? RUNTIME_RUN_ID;
    let run = runs.get(runId);
    if (!run) {
      run = {
        id: runId,
        source: event.payload.runId === null ? "runtime" : "run",
        worktree: null,
        issue: null,
        command: null,
        state: "unknown",
        status: "unknown",
        durationMs: null,
        startedCursor: null,
        finishedCursor: null,
        steps: [],
        receipts: [],
      };
      runs.set(runId, run);
    }
    if (event.payload.issue !== null) {
      run.issue = run.issue ?? event.payload.issue;
      run.worktree = run.worktree ?? event.payload.issue;
    }
    if (event.kind === "run.started") {
      run.startedCursor = run.startedCursor ?? event.cursor;
      run.command = run.command ?? event.payload.command;
    }
    if (event.kind === "run.finished") {
      run.finishedCursor = event.cursor;
      run.status = event.payload.status ?? "unknown";
      if (event.payload.durationMs !== null) run.durationMs = event.payload.durationMs;
      if (event.payload.receiptId !== null) {
        if (!run.receipts.includes(event.payload.receiptId)) run.receipts.push(event.payload.receiptId);
        receipts.push({ runId, receiptId: event.payload.receiptId, cursor: event.cursor });
      }
    }
    const step = createStep(event, run.steps.length + 1);
    redactions += step.redactions;
    run.steps.push(step);
  }

  const orderedRuns = [...runs.values()].sort((left, right) => {
    const leftCursor = left.steps[0]?.cursor ?? 0;
    const rightCursor = right.steps[0]?.cursor ?? 0;
    return leftCursor - rightCursor || left.id.localeCompare(right.id);
  });
  for (const run of orderedRuns) {
    run.state = run.finishedCursor !== null ? "finished" : run.startedCursor !== null ? "running" : "unknown";
  }

  return {
    schema: REPLAY_SCHEMA,
    generatedAt,
    streamId: page.streamId,
    eventCount: events.length,
    rejectedEvents: page.rejected ?? 0,
    headCursor: page.headCursor,
    redactions,
    runs: orderedRuns,
    receipts,
  };
}

export interface AiBomOptions {
  source?: "runtime" | "preview";
  generatedAt?: string;
}

export function buildAiBom(replay: ActivityReplay, options: AiBomOptions = {}): AiBom {
  const runs: AiBomRun[] = replay.runs.map((run) => ({
    id: run.id,
    source: run.source,
    worktree: run.worktree,
    state: run.state,
    status: run.status,
    command: run.command,
    durationMs: run.durationMs,
    receipts: [...run.receipts],
    steps: run.steps.map((step) => ({
      sequence: step.sequence,
      cursor: step.cursor,
      kind: step.kind,
      status: step.status,
      detail: step.detail,
      receiptId: step.receiptId,
    })),
  }));
  const allSteps = runs.flatMap((run) => run.steps);
  const source = options.source ?? "runtime";
  return {
    schema: AI_BOM_SCHEMA,
    generatedAt: options.generatedAt ?? new Date().toISOString(),
    source,
    provenance: {
      producer: "simplicio-desktop",
      source,
      eventSchema: EVENT_SCHEMA,
      streamId: replay.streamId,
      firstCursor: replay.runs[0]?.steps[0]?.cursor ?? null,
      lastCursor: replay.runs.at(-1)?.steps.at(-1)?.cursor ?? null,
      eventCount: replay.eventCount,
      rejectedEvents: replay.rejectedEvents,
      stepCount: allSteps.length,
      receiptCount: replay.receipts.length,
      replayGeneratedAt: replay.generatedAt,
      redaction: {
        schema: REDACTION_SCHEMA,
        prompts: true,
        credentials: true,
        paths: true,
        unknownFields: "dropped",
        redactionsApplied: replay.redactions,
      },
    },
    summary: {
      runs: runs.length,
      finished: runs.filter((run) => run.state === "finished").length,
      running: runs.filter((run) => run.state === "running").length,
      receipts: replay.receipts.length,
      redactions: replay.redactions,
    },
    runs,
  };
}

export function aiBomToJson(bom: AiBom): string {
  return JSON.stringify(bom, null, 2);
}

function markdownCell(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
}

export function aiBomToMarkdown(bom: AiBom): string {
  const lines: string[] = [
    "# AI-BOM — Simplicio Desktop",
    "",
    `- Schema: \`${bom.schema}\``,
    `- Generated: ${bom.generatedAt}`,
    `- Source: ${bom.source}`,
    `- Event schema: \`${bom.provenance.eventSchema}\``,
    `- Stream: ${bom.provenance.streamId === null ? "unknown" : `\`${bom.provenance.streamId}\``}`,
    `- Cursors: ${bom.provenance.firstCursor ?? "unknown"}–${bom.provenance.lastCursor ?? "unknown"}`,
    `- Events: ${bom.provenance.eventCount} (rejected: ${bom.provenance.rejectedEvents})`,
    `- Runs: ${bom.summary.runs} (finished: ${bom.summary.finished}, running: ${bom.summary.running})`,
    `- Receipts: ${bom.summary.receipts}`,
    `- Redaction: prompts, credentials and paths; ${bom.summary.redactions} redaction(s) applied`,
    "",
  ];
  for (const run of bom.runs) {
    lines.push(`## Run \`${run.id}\``, "");
    lines.push(`- Source: ${run.source}`);
    lines.push(`- Worktree: ${run.worktree ?? "unknown"}`);
    lines.push(`- State: ${run.state}`);
    lines.push(`- Status: ${run.status}`);
    lines.push(`- Command: ${run.command ?? "unknown"}`);
    lines.push(`- Duration: ${run.durationMs === null ? "unknown" : `${run.durationMs} ms`}`);
    lines.push(`- Receipts: ${run.receipts.length === 0 ? "unknown" : run.receipts.map((id) => `\`${id}\``).join(", ")}`);
    lines.push("", "| # | Cursor | Event | Status | Detail |", "| - | ------ | ----- | ------ | ------ |");
    for (const step of run.steps) {
      lines.push(`| ${step.sequence} | ${step.cursor} | \`${step.kind}\` | ${markdownCell(step.status)} | ${markdownCell(step.detail ?? "unknown")} |`);
    }
    lines.push("");
  }
  lines.push("> Unknown or absent fields are reported as `unknown`; they are never inferred.", "");
  return lines.join("\n");
}

/** UTF-8 byte length without depending on Node buffers or Blob. */
export function utf8Bytes(text: string): number {
  let bytes = 0;
  for (let index = 0; index < text.length; index += 1) {
    const code = text.charCodeAt(index);
    if (code < 0x80) bytes += 1;
    else if (code < 0x800) bytes += 2;
    else if (code >= 0xd800 && code <= 0xdbff) {
      bytes += 4;
      index += 1;
    } else bytes += 3;
  }
  return bytes;
}
