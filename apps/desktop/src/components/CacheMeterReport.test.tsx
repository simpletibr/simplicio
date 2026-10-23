import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { CacheMeterReport } from "./CacheMeterReport";
import type { CacheMeterReceipt } from "../cache_meter";

const receipt = (overrides: Partial<CacheMeterReceipt> = {}): CacheMeterReceipt => ({
  schema: "simplicio.cache-meter/v1",
  status: "measured",
  requests: 2,
  session_hit_rate: 0.995,
  tolerance_tokens: 16,
  ttl_secs: 300,
  busts: [{
    request_index: 1,
    expected_read: 100,
    actual_read: 40,
    attribution: ["ttl_gap", "model_switch"],
  }],
  per_request: [
    { index: 0, model: "m", input: 10, read: 90, write: 0, request_share: 0.9, cumulative_share: 0.9, prefix_reuse: 0.9 },
    { index: 1, model: "m2", input: 20, read: 40, write: 0, request_share: 0.66, cumulative_share: 0.81, prefix_reuse: 0.66 },
  ],
  ...overrides,
});

describe("CacheMeterReport", () => {
  it("shows the measured hit rate, prefix reuse and attributed breaks", () => {
    const html = renderToStaticMarkup(<CacheMeterReport receipt={receipt()} />);
    expect(html).toContain("99.5%");
    expect(html).toContain("66%");
    expect(html).toContain("intervalo TTL");
    expect(html).toContain("troca de modelo");
    expect(html).toContain("simplicio.cache-meter/v1");
  });

  it("hides the number when the session is unmeasured or has no billed input", () => {
    const unmeasured = renderToStaticMarkup(<CacheMeterReport receipt={receipt({ status: "unmeasured", session_hit_rate: null, requests: 0, busts: [], per_request: [] })} />);
    expect(unmeasured).toBe("");
    const empty = renderToStaticMarkup(<CacheMeterReport receipt={receipt({
      session_hit_rate: 0,
      per_request: [
        { index: 0, model: null, input: 0, read: 0, write: 0, request_share: null, cumulative_share: null, prefix_reuse: null },
      ],
    })} />);
    expect(empty).toBe("");
  });

  it("names an unavailable meter without inventing a rate", () => {
    const html = renderToStaticMarkup(<CacheMeterReport error="cache_meter_unavailable" />);
    expect(html).toContain("indisponível");
    expect(html).not.toContain("%");
  });
});
