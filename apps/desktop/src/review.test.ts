import { describe, expect, it } from "vitest";
import {
  autoMergeLabel,
  parseReviewReceipt,
  reviewView,
  type ReviewDigest,
  type ReviewSubmissionReceipt,
} from "./review";

const DIGEST = "sha256:" + "a".repeat(64);
const OTHER_DIGEST = "sha256:" + "b".repeat(64);

const cleanDiff = [
  "diff --git a/src/a.ts b/src/a.ts",
  "--- a/src/a.ts",
  "+++ b/src/a.ts",
  "@@ -1 +1,2 @@",
  "-old",
  "+new",
  "+extra",
].join("\n");

const protectedDiff = [
  cleanDiff,
  "diff --git a/install.sh b/install.sh",
  "--- a/install.sh",
  "+++ b/install.sh",
  "@@ -1 +1 @@",
  "-a",
  "+b",
].join("\n");

function review(overrides: Partial<ReviewDigest> = {}): ReviewDigest {
  return {
    schema: "simplicio.desktop-review/v1",
    repo: "C:/repo",
    base: null,
    status: "",
    diff: cleanDiff,
    digest: DIGEST,
    truncated: false,
    ...overrides,
  };
}

function reason(view: ReviewDigest, plan?: string | null) {
  return reviewView(view, plan).autoMerge;
}

describe("auto-merge eligibility", () => {
  it("is eligible only with a matching plan digest and no guardrail", () => {
    expect(reason(review(), DIGEST)).toEqual({ eligible: true, reason: "eligible" });
    expect(reason(review(), "  " + DIGEST.toUpperCase() + "  ")).toEqual({ eligible: true, reason: "eligible" });
  });

  it("reports a missing plan digest instead of claiming eligibility", () => {
    expect(reason(review())).toEqual({ eligible: false, reason: "plan_digest_missing" });
    expect(reason(review(), "   ")).toEqual({ eligible: false, reason: "plan_digest_missing" });
  });

  it("reports a plan digest mismatch", () => {
    expect(reason(review(), OTHER_DIGEST)).toEqual({ eligible: false, reason: "plan_digest_mismatch" });
    expect(reason(review(), "not-a-digest")).toEqual({ eligible: false, reason: "plan_digest_mismatch" });
  });

  it("blocks protected paths even with a matching plan digest", () => {
    expect(reason(review({ diff: protectedDiff }), DIGEST)).toEqual({ eligible: false, reason: "protected_path" });
    expect(reason(review({ diff: protectedDiff }))).toEqual({ eligible: false, reason: "protected_path" });
  });

  it("blocks truncated diffs before any other reason", () => {
    expect(reason(review({ diff: protectedDiff, truncated: true }), DIGEST)).toEqual({ eligible: false, reason: "truncated" });
    expect(reason(review({ truncated: true }))).toEqual({ eligible: false, reason: "truncated" });
  });

  it("labels the real reason for the badge", () => {
    expect(autoMergeLabel({ eligible: true, reason: "eligible" })).toBe("auto-merge elegível");
    expect(autoMergeLabel({ eligible: false, reason: "plan_digest_mismatch" })).toBe("auto-merge: plan_digest_mismatch");
    expect(autoMergeLabel({ eligible: false, reason: "truncated" })).toBe("auto-merge: truncated");
  });
});

const receipt: ReviewSubmissionReceipt = {
  schema: "simplicio.review-receipt/v1",
  receipt_id: "review-" + "c".repeat(24),
  path: ".simplicio/review-inbox/sha256-" + "a".repeat(64) + ".json",
  entry_digest: "sha256:" + "d".repeat(64),
  digest: DIGEST,
  comments_digest: "sha256:" + "e".repeat(64),
  comments_bytes: 42,
  plan_digest: DIGEST,
  auto_merge: { eligible: true, reason: "eligible" },
  idempotent: false,
  redacted: true,
};

describe("review receipt", () => {
  it("parses the versioned native receipt", () => {
    expect(parseReviewReceipt(receipt)).toEqual(receipt);
  });

  it("rejects a receipt whose eligibility contradicts its reason", () => {
    expect(() => parseReviewReceipt({ ...receipt, auto_merge: { eligible: true, reason: "protected_path" } })).toThrow(
      "review_receipt_invalid",
    );
    expect(() => parseReviewReceipt({ ...receipt, schema: "simplicio.review-receipt/v2" })).toThrow(
      "review_receipt_invalid",
    );
    expect(() => parseReviewReceipt(null)).toThrow("review_receipt_invalid");
  });
});
