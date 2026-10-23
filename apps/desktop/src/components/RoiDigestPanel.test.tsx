import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import type { CostProjection } from "../cost_projection";
import { buildRoiDigest, weeklyWindow } from "../roi_digest";
import { RoiDigestCard } from "../components/RoiDigestPanel";

const projection = {
  schema: "simplicio.desktop-cost-projection/v1",
  generated_at_epoch: 100,
  query: {},
  usage_revision: "rev-1",
  pricing: { status: "known", identity: "catalog", version: "1", versions: ["1"], sources: [] },
  baseline: { identity_status: "unknown", versions: [], methods: [], values_status: "unavailable", reason: "baseline_values_not_recorded" },
  confidence: { actual: "high", baseline: "blocked", savings: "blocked" },
  rows: [
    { provider: "claude", model: "m", host: "claude-code", project_id: "p", session_id: "s", execution: "remote", state: "measured", confidence: "high", reason: null, event_count: 1, actual_tokens: 100, actual_cost_usd: 0.1, baseline_tokens: null, baseline_cost_usd: null, saved_tokens: null, saved_cost_usd: null },
    { provider: "codex", model: "m2", host: "codex", project_id: "p", session_id: "s", execution: "remote", state: "estimated", confidence: "blocked", reason: "baseline_values_not_recorded", event_count: 1, actual_tokens: null, actual_cost_usd: null, baseline_tokens: null, baseline_cost_usd: null, saved_tokens: null, saved_cost_usd: null },
  ],
  totals: { event_count: 2, actual_tokens: 100, actual_cost_usd: 0.1, baseline_tokens: null, baseline_cost_usd: null, saved_tokens: null, saved_cost_usd: null },
  metadata: { source: "runtime", generated_by: "runtime_usage_ledger", revision: "r", report_digest: "sha256:" + "a".repeat(64), coverage: { status: "partial", missing_usage_events: 1, unpriced_events: 0, providers: ["claude"], reason: null }, redacted: true },
} as unknown as CostProjection;

describe("ROI digest", () => {
  it("keeps estimated rows out of the measured section and unknown values as —", () => {
    const window = weeklyWindow(10 * 24 * 60 * 60);
    const digest = buildRoiDigest(projection, window);
    expect(digest.measuredRows).toBe(1);
    expect(digest.estimatedRows).toBe(1);
    expect(digest.markdown).toContain("## Medido / provider-reported");
    expect(digest.markdown).toContain("## Estimado (não é medição)");
    expect(digest.markdown).toContain("—");
    const measuredSection = digest.markdown.split("## Estimado")[0];
    expect(measuredSection).not.toContain("codex");
    const html = renderToStaticMarkup(<RoiDigestCard digest={digest} />);
    expect(html).toContain("Digest semanal");
    expect(html).toContain("Baixar Markdown");
  });
});
