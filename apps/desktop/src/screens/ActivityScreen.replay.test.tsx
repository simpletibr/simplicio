import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { createDemoSnapshot } from "../demo";
import { EVENT_SCHEMA, EVENTS_PAGE_SCHEMA, parseEventPage } from "../activity_replay";
import { ActivityScreen } from "./ActivityScreen";

const page = parseEventPage({
  schema: EVENTS_PAGE_SCHEMA,
  stream_id: "stream-1",
  events: [
    {
      schema: EVENT_SCHEMA,
      event: "run.started",
      cursor: 1,
      payload: { run_id: "run-1", issue: "issue-432", command: "map" },
    },
    {
      schema: EVENT_SCHEMA,
      event: "run.progress",
      cursor: 2,
      payload: { run_id: "run-1", message: "token=segredo-nao-pode-vazar" },
    },
    {
      schema: EVENT_SCHEMA,
      event: "run.finished",
      cursor: 3,
      payload: { run_id: "run-1", status: "ok", duration_ms: 1200, receipt_id: "receipt-1" },
    },
  ],
  next_cursor: 3,
  has_more: false,
  head_cursor: 3,
  retention_window: 4096,
});

describe("Activity replay section", () => {
  it("renders the recorded run, ordered steps, receipts and export controls", () => {
    const html = renderToStaticMarkup(
      <ActivityScreen snapshot={createDemoSnapshot("active")} initialEvents={page} />,
    );
    expect(html).toContain('data-testid="activity-replay"');
    expect(html).toContain("Replay da execução");
    expect(html).toContain("run-1");
    expect(html).toContain("issue-432");
    expect(html).toContain("run.started");
    expect(html).toContain("receipt-1");
    expect(html).toContain("AI-BOM (JSON)");
    expect(html).toContain("AI-BOM (Markdown)");
    expect(html).toContain("3 evento(s)");
    expect(html).toContain("3 de 3 passo(s)");
  });

  it("redacts secret-shaped content before it reaches the DOM", () => {
    const html = renderToStaticMarkup(
      <ActivityScreen snapshot={createDemoSnapshot("active")} initialEvents={page} />,
    );
    expect(html).not.toContain("segredo-nao-pode-vazar");
    expect(html).toContain("[redacted-secret]");
  });

  it("does not fabricate a replay when no daemon page is available", () => {
    const html = renderToStaticMarkup(
      <ActivityScreen snapshot={createDemoSnapshot("active")} />,
    );
    expect(html).toContain("Sem eventos do daemon para reproduzir");
    expect(html).not.toContain("run.started");
    expect(html).toContain('disabled=""');
  });
});
