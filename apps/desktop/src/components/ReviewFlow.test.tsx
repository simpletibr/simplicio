import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ReviewFlowCard } from "./ReviewFlow";
import { parseUnifiedDiff, reviewFlags, reviewView, type ReviewDigest, type ReviewSubmissionReceipt } from "../review";

const diff = [
  "diff --git a/src/a.ts b/src/a.ts",
  "--- a/src/a.ts",
  "+++ b/src/a.ts",
  "@@ -1,2 +1,3 @@",
  "-old",
  "+new",
  "+extra",
  "diff --git a/install.sh b/install.sh",
  "--- a/install.sh",
  "+++ b/install.sh",
  "@@ -1 +1 @@",
  "-a",
  "+b",
].join("\n");

const review: ReviewDigest = {
  schema: "simplicio.desktop-review/v1",
  repo: "C:/repo",
  base: null,
  status: "",
  diff,
  digest: "sha256:" + "a".repeat(64),
  truncated: false,
};

const receipt: ReviewSubmissionReceipt = {
  schema: "simplicio.review-receipt/v1",
  receipt_id: "review-" + "c".repeat(24),
  path: ".simplicio/review-inbox/sha256-" + "a".repeat(64) + ".json",
  entry_digest: "sha256:" + "d".repeat(64),
  digest: review.digest,
  comments_digest: "sha256:" + "e".repeat(64),
  comments_bytes: 12,
  plan_digest: null,
  auto_merge: { eligible: false, reason: "plan_digest_missing" },
  idempotent: false,
  redacted: true,
};

function render(overrides: Partial<Parameters<typeof ReviewFlowCard>[0]> = {}) {
  return renderToStaticMarkup(
    <ReviewFlowCard
      review={review}
      comments="fix this"
      planDigest=""
      receipt={null}
      busy={false}
      onComments={() => undefined}
      onCopy={() => undefined}
      onSubmit={() => undefined}
      {...overrides}
    />,
  );
}

describe("ReviewFlow", () => {
  it("parses files, flags protected paths and never claims auto-merge without a plan", () => {
    const files = parseUnifiedDiff(diff);
    expect(files.map((file) => file.path)).toEqual(["src/a.ts", "install.sh"]);
    expect(files[0].additions).toBe(2);
    expect(reviewFlags(files)).toEqual([{ path: "install.sh", kind: "protected" }]);
    const view = reviewView(review);
    expect(view.autoMerge.eligible).toBe(false);
    expect(view.autoMerge.reason).toBe("protected_path");
    const html = render();
    expect(html).toContain("install.sh");
    expect(html).toContain("protected");
    expect(html).toContain("auto-merge: protected_path");
    expect(html).toContain("Enviar ao agente");
  });

  it("shows the real truncated reason before any plan claim", () => {
    const html = render({ review: { ...review, diff, truncated: true }, planDigest: review.digest });
    expect(html).toContain("auto-merge: truncated");
    expect(html).not.toContain("auto-merge elegível");
    expect(html).toContain("Diff truncado em 200 KB");
  });

  it("shows the inbox receipt without claiming a live agent session", () => {
    const html = render({ receipt, comments: "fix this" });
    expect(html).toContain("review-" + "c".repeat(24));
    expect(html).toContain(".simplicio/review-inbox/sha256-");
    expect(html).toContain("auto-merge: plan_digest_missing");
    expect(html).toContain("O agente não é notificado em tempo real");
    expect(html).toContain("a skill do agente o lê antes do próximo turno");
  });

  it("surfaces submission errors in the card", () => {
    const html = render({ submitError: "review_digest_mismatch" });
    expect(html).toContain("O diff mudou desde que foi carregado");
  });
});
