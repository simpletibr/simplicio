import { describe, expect, it } from "vitest";
import {
  ORIENTATION_BUDGET_MS,
  ORIENTATION_SCHEMA,
  WORKTREE_CREATE_SCHEMA,
  orientationFields,
  orientationNotice,
  parseOrientation,
  parseWorktreeCreateReceipt,
} from "./worktree_orientation";

function measured(overrides: Record<string, unknown> = {}) {
  return {
    schema: ORIENTATION_SCHEMA,
    status: "measured",
    generation: "baseline+delta",
    orientation_ms: 412,
    baseline_build_ms: 380,
    mapped_files: 673,
    cache_state: "hit",
    baseline_reused: true,
    within_budget: true,
    ...overrides,
  };
}

describe("worktree orientation contract", () => {
  it("keeps a measured orientation and derives the budget from the number", () => {
    const parsed = parseOrientation(measured());
    expect(parsed.status).toBe("measured");
    expect(parsed.orientation_ms).toBe(412);
    expect(parsed.generation).toBe("baseline+delta");
    expect(parsed.baseline_reused).toBe(true);
    expect(parsed.within_budget).toBe(true);
    expect(orientationNotice(parsed)).toBeNull();

    const slow = parseOrientation(measured({ orientation_ms: ORIENTATION_BUDGET_MS }));
    expect(slow.within_budget).toBe(false);

    // A payload that claims the budget while reporting more ms is corrected.
    const lying = parseOrientation(measured({ orientation_ms: 9_000, within_budget: true }));
    expect(lying.within_budget).toBe(false);
  });

  it("never fabricates a measurement for a failed orientation", () => {
    const missing = parseOrientation({
      schema: ORIENTATION_SCHEMA,
      status: "baseline_missing",
      error: "orientation_baseline_missing",
      orientation_ms: null,
      baseline_reused: false,
      within_budget: false,
      hint: "rode simplicio map",
    });
    expect(missing.orientation_ms).toBeNull();
    expect(missing.within_budget).toBe(false);
    expect(orientationNotice(missing)).toContain("Baseline ausente");

    expect(() => parseOrientation({ ...missing, status: "baseline_missing", orientation_ms: 300 })).toThrow("orientation_invalid");
    expect(() => parseOrientation({ schema: "other", status: "measured" })).toThrow("orientation_invalid");
    expect(() => parseOrientation(measured({ orientation_ms: -1 }))).toThrow("orientation_invalid");
    expect(() => parseOrientation(measured({ orientation_ms: 1.5 }))).toThrow("orientation_invalid");
    expect(() => parseOrientation(measured({ generation: "remap" }))).toThrow("orientation_invalid");
    expect(() => parseOrientation(measured({ baseline_reused: false }))).toThrow("orientation_invalid");
    expect(() => parseOrientation({ schema: ORIENTATION_SCHEMA, status: "paused" })).toThrow("orientation_invalid");
  });

  it("parses the worktree create receipt together with its orientation", () => {
    const receipt = parseWorktreeCreateReceipt({
      schema: WORKTREE_CREATE_SCHEMA,
      status: "created",
      issue: 433,
      branch: "issue-433",
      path: "/tmp/worktrees/repo/issue-433",
      redacted: true,
      orientation: measured({ orientation_ms: 295 }),
    });
    expect(receipt.issue).toBe(433);
    expect(receipt.branch).toBe("issue-433");
    expect(receipt.orientation.orientation_ms).toBe(295);

    const missing = parseWorktreeCreateReceipt({
      schema: WORKTREE_CREATE_SCHEMA,
      status: "created",
      issue: 434,
      branch: "issue-434",
      path: "/tmp/worktrees/repo/issue-434",
      orientation: { schema: ORIENTATION_SCHEMA, status: "baseline_missing", orientation_ms: null, baseline_reused: false },
    });
    expect(missing.orientation.orientation_ms).toBeNull();

    expect(() => parseWorktreeCreateReceipt({ schema: "other" })).toThrow("worktree_create_invalid");
    expect(() =>
      parseWorktreeCreateReceipt({
        schema: WORKTREE_CREATE_SCHEMA,
        issue: 0,
        path: "/tmp/x",
        orientation: measured(),
      }),
    ).toThrow("worktree_create_invalid");
  });
});

describe("fleet task fields", () => {
  it("carries the measured duration and nothing for an unmeasured one", () => {
    const measuredTask = orientationFields(parseOrientation(measured({ orientation_ms: 733 })));
    expect(measuredTask).toEqual({ orientation_ms: 733 });

    const missing = parseOrientation({
      schema: ORIENTATION_SCHEMA,
      status: "baseline_missing",
      orientation_ms: null,
      baseline_reused: false,
    });
    expect(orientationFields(missing)).toEqual({});
    expect(orientationFields(undefined)).toEqual({});
    expect(orientationFields(null)).toEqual({});
  });
});
