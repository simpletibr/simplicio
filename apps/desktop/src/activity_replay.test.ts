import { describe, expect, it } from "vitest";
import {
  AI_BOM_SCHEMA,
  EVENT_SCHEMA,
  EVENTS_PAGE_SCHEMA,
  MAX_CURSOR,
  MAX_EVENTS,
  REPLAY_SCHEMA,
  aiBomToJson,
  aiBomToMarkdown,
  buildAiBom,
  createReplay,
  mergeEventPages,
  parseDesktopEvent,
  parseEventPage,
  redactText,
  type DesktopEventPage,
} from "./activity_replay";

function envelope(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    schema: EVENT_SCHEMA,
    event: "run.progress",
    cursor: 1,
    payload: { run_id: "run-1", message: "map: 12 arquivos" },
    ...overrides,
  };
}

function rawPage(events: unknown[], overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    schema: EVENTS_PAGE_SCHEMA,
    stream_id: "stream-1",
    events,
    next_cursor: events.length,
    has_more: false,
    head_cursor: events.length,
    retention_window: 4096,
    ...overrides,
  };
}

function recordedPage(): DesktopEventPage {
  return parseEventPage(rawPage([
    envelope({
      event: "run.finished",
      cursor: 3,
      payload: { run_id: "run-1", status: "ok", duration_ms: 1200, receipt_id: "receipt-1" },
    }),
    envelope({ cursor: 1, event: "run.started", payload: { run_id: "run-1", issue: "issue-432", command: "map" } }),
    envelope({ cursor: 2 }),
    envelope({
      event: "plugin.installed",
      cursor: 4,
      payload: { plugin_id: "simplicio-loop", version: "1.2.0" },
    }),
  ]));
}

describe("desktop event parser", () => {
  it("accepts the runtime envelope and the legacy singular alias", () => {
    expect(parseDesktopEvent(envelope()).schema).toBe(EVENT_SCHEMA);
    expect(parseDesktopEvent(envelope({ schema: "simplicio.desktop-event/v1" })).schema).toBe(EVENT_SCHEMA);
  });

  it("rejects wrong schemas, unknown kinds, cursors and payloads fail-closed", () => {
    const codes = (value: unknown) => {
      try {
        parseDesktopEvent(value);
        return "accepted";
      } catch (error) {
        return (error as { code?: string }).code;
      }
    };
    expect(codes(envelope({ schema: "simplicio.activity-export/v1" }))).toBe("unsupported_schema");
    expect(codes(envelope({ event: "run.invented" }))).toBe("unknown_event_kind");
    expect(codes(envelope({ cursor: -1 }))).toBe("invalid_cursor");
    expect(codes(envelope({ cursor: 1.5 }))).toBe("invalid_cursor");
    expect(codes(envelope({ cursor: MAX_CURSOR + 1 }))).toBe("invalid_cursor");
    expect(codes(envelope({ payload: { message: "sem run" } }))).toBe("invalid_payload");
    expect(codes(envelope({ payload: { run_id: "run-1", message: "linha\nquebrada" } }))).toBe("invalid_payload");
    expect(codes([1, 2, 3])).toBe("invalid_envelope");
  });

  it("drops undocumented payload fields instead of inventing provenance", () => {
    const parsed = parseDesktopEvent(envelope({
      payload: { run_id: "run-1", message: "ok", saved_tokens: 42, secret_hint: "keep-out" },
    }));
    expect(JSON.stringify(parsed)).not.toContain("saved_tokens");
    expect(JSON.stringify(parsed)).not.toContain("secret_hint");
  });
});

describe("replay projection", () => {
  it("orders by cursor and collapses duplicate cursors deterministically", () => {
    const forward = parseEventPage(rawPage([
      envelope({ cursor: 2, payload: { run_id: "run-1", message: "b" } }),
      envelope({ cursor: 2, payload: { run_id: "run-1", message: "a" } }),
      envelope({ cursor: 1, event: "run.started", payload: { run_id: "run-1", command: "map" } }),
    ]));
    const reversed = parseEventPage(rawPage([
      envelope({ cursor: 1, event: "run.started", payload: { run_id: "run-1", command: "map" } }),
      envelope({ cursor: 2, payload: { run_id: "run-1", message: "a" } }),
      envelope({ cursor: 2, payload: { run_id: "run-1", message: "b" } }),
    ]));
    expect(forward.events.map((event) => event.cursor)).toEqual([1, 2]);
    expect(forward.events[1].payload.message).toBe("a");
    expect(createReplay(forward, "2026-01-01T00:00:00.000Z").runs)
      .toEqual(createReplay(reversed, "2026-01-01T00:00:00.000Z").runs);
  });

  it("reconstructs ordered steps per run with worktree and receipts", () => {
    const replay = createReplay(recordedPage(), "2026-01-01T00:00:00.000Z");
    expect(replay.schema).toBe(REPLAY_SCHEMA);
    expect(replay.streamId).toBe("stream-1");
    const [run, runtime] = replay.runs;
    expect(run.id).toBe("run-1");
    expect(run.source).toBe("run");
    expect(run.worktree).toBe("issue-432");
    expect(run.state).toBe("finished");
    expect(run.status).toBe("ok");
    expect(run.durationMs).toBe(1200);
    expect(run.steps.map((step) => step.kind)).toEqual(["run.started", "run.progress", "run.finished"]);
    expect(run.steps.map((step) => step.sequence)).toEqual([1, 2, 3]);
    expect(run.steps[1].status).toBe("unknown");
    expect(run.receipts).toEqual(["receipt-1"]);
    expect(replay.receipts).toEqual([{ runId: "run-1", receiptId: "receipt-1", cursor: 3 }]);
    expect(runtime.id).toBe("runtime");
    expect(runtime.source).toBe("runtime");
    expect(runtime.steps[0].kind).toBe("plugin.installed");
  });

  it("keeps a run without a finish as running and without a start as unknown", () => {
    const replay = createReplay(parseEventPage(rawPage([
      envelope({ cursor: 1, event: "run.started", payload: { run_id: "a" } }),
      envelope({ cursor: 2, payload: { run_id: "b", message: "sem início" } }),
    ])), "2026-01-01T00:00:00.000Z");
    expect(replay.runs.find((run) => run.id === "a")?.state).toBe("running");
    expect(replay.runs.find((run) => run.id === "b")?.state).toBe("unknown");
  });
});

describe("AI-BOM export", () => {
  const secretMessage = "token=plain-secret sk-abcdefgh12345678 wesley@example.test /Users/wesley/private/repo";

  function bom() {
    const page = parseEventPage(rawPage([
      envelope({ cursor: 1, event: "run.started", payload: { run_id: "run-1", issue: "issue-432", command: "map" } }),
      envelope({ cursor: 2, payload: { run_id: "run-1", message: secretMessage } }),
      envelope({ cursor: 3, event: "run.finished", payload: { run_id: "run-1", status: "ok", receipt_id: "receipt-1" } }),
    ]));
    return buildAiBom(createReplay(page, "2026-01-01T00:00:00.000Z"), {
      source: "runtime",
      generatedAt: "2026-01-02T00:00:00.000Z",
    });
  }

  it("carries schema, provenance and redacted step content", () => {
    const value = bom();
    expect(value.schema).toBe(AI_BOM_SCHEMA);
    expect(value.source).toBe("runtime");
    expect(value.provenance).toMatchObject({
      producer: "simplicio-desktop",
      source: "runtime",
      eventSchema: EVENT_SCHEMA,
      streamId: "stream-1",
      firstCursor: 1,
      lastCursor: 3,
      eventCount: 3,
      rejectedEvents: 0,
      stepCount: 3,
      receiptCount: 1,
      replayGeneratedAt: "2026-01-01T00:00:00.000Z",
    });
    expect(value.provenance.redaction).toMatchObject({ credentials: true, prompts: true, paths: true });
    expect(value.summary).toMatchObject({ runs: 1, finished: 1, running: 0, receipts: 1 });
    expect(value.runs[0].receipts).toEqual(["receipt-1"]);
    expect(value.runs[0].steps[0].status).toBe("unknown");
  });

  it("redacts secrets, e-mail and private paths in JSON and Markdown", () => {
    const json = aiBomToJson(bom());
    const markdown = aiBomToMarkdown(bom());
    for (const output of [json, markdown]) {
      expect(output).not.toContain("plain-secret");
      expect(output).not.toContain("sk-abcdefgh12345678");
      expect(output).not.toContain("wesley@example.test");
      expect(output).not.toContain("/Users/wesley/private/repo");
      expect(output).toContain(AI_BOM_SCHEMA);
    }
    expect(markdown).toContain("## Run `run-1`");
    expect(markdown).toContain("receipt-1");
    expect(markdown).toContain("> Unknown or absent fields are reported as `unknown`");
    expect(JSON.parse(json).provenance.redaction.redactionsApplied).toBeGreaterThan(0);
  });

  it("counts redactions and leaves clean text untouched", () => {
    expect(redactText("map: 12 arquivos")).toEqual({ text: "map: 12 arquivos", redactions: 0 });
    const result = redactText("Bearer abcdefgh12345678");
    expect(result.redactions).toBe(1);
    expect(result.text).toBe("Bearer [redacted-secret]");
  });
});

describe("bounded pages and merge", () => {
  it("caps a page at the requested limit without dropping the resume cursor", () => {
    const page = parseEventPage(rawPage([
      envelope({ cursor: 1 }),
      envelope({ cursor: 2 }),
      envelope({ cursor: 3 }),
    ]), 2);
    expect(page.events).toHaveLength(2);
    expect(page.rejected).toBe(0);
    expect(page.hasMore).toBe(true);
    expect(page.nextCursor).toBe(2);
  });

  it("rejects more than 500 events and pages over 1 MB", () => {
    const tooMany = Array.from({ length: MAX_EVENTS + 1 }, (_, index) => envelope({ cursor: index }));
    expect(() => parseEventPage(rawPage(tooMany))).toThrowError(expect.objectContaining({ code: "page_too_many_events" }));
    expect(() => parseEventPage(rawPage([envelope()], { padding: "x".repeat(1_100_000) })))
      .toThrowError(expect.objectContaining({ code: "page_too_large" }));
  });

  it("counts malformed events as rejected instead of rendering them", () => {
    const page = parseEventPage(rawPage([envelope({ cursor: 1 }), envelope({ cursor: "2" })]));
    expect(page.events).toHaveLength(1);
    expect(page.rejected).toBe(1);
  });

  it("merges pages without duplicating a cursor", () => {
    const first = parseEventPage(rawPage([envelope({ cursor: 1 }), envelope({ cursor: 2 })]));
    const second = parseEventPage(rawPage([
      envelope({ cursor: 2 }),
      envelope({ cursor: 3, event: "run.finished", payload: { run_id: "run-1", status: "ok" } }),
    ]));
    const merged = mergeEventPages(first, second);
    expect(merged.events.map((event) => event.cursor)).toEqual([1, 2, 3]);
    expect(merged.nextCursor).toBe(3);
  });
});
