import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ReviewFlowCard } from "./ReviewFlow";
import {
  commitGuard,
  commitGuardLabel,
  commitMessageError,
  parseReviewCommitReceipt,
  parseReviewPushReceipt,
  parseUnifiedDiff,
  reviewFlags,
  reviewView,
  type ReviewCommitReceipt,
  type ReviewDigest,
  type ReviewPushReceipt,
  type ReviewSubmissionReceipt,
} from "../review";

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

const cleanReview: ReviewDigest = {
  ...review,
  diff: [
    "diff --git a/src/a.ts b/src/a.ts",
    "--- a/src/a.ts",
    "+++ b/src/a.ts",
    "@@ -1 +1 @@",
    "-old",
    "+new",
  ].join("\n"),
};

const sha = "f".repeat(40);

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

const commitReceipt: ReviewCommitReceipt = {
  schema: "simplicio.desktop-review-commit/v1",
  status: "committed",
  receipt_id: "commit-" + "f".repeat(24),
  path: ".simplicio/review-commits/" + "a".repeat(64) + "--" + sha + ".json",
  digest: review.digest,
  sha,
  branch: "issue-469",
  paths: ["src/a.ts"],
  message_chars: 18,
  message_digest: "sha256:" + "1".repeat(64),
  upstream: null,
  pushed: false,
  phase: "committed",
  code: null,
  stderr: null,
  redacted: true,
};

const failedCommit: ReviewCommitReceipt = {
  ...commitReceipt,
  status: "commit_failed",
  receipt_id: null,
  path: null,
  sha: null,
  phase: "failed",
  code: "review_commit_failed",
  stderr: "pre-commit: lint failed on a.txt",
};

const failedPush: ReviewPushReceipt = {
  schema: "simplicio.desktop-review-push/v1",
  status: "push_failed",
  sha,
  branch: "issue-469",
  upstream: null,
  idempotent: false,
  code: "review_push_failed",
  stderr: "! [rejected] issue-469 -> issue-469 (non-fast-forward)",
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
      commitMessage="feat: reviewed change"
      commitConfirmed={true}
      createUpstream={false}
      commitReceipt={null}
      pushReceipt={null}
      onCommitMessage={() => undefined}
      onCommitConfirmed={() => undefined}
      onCreateUpstream={() => undefined}
      onCommit={() => undefined}
      onPush={() => undefined}
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

  it("blocks the commit when the review has a protected path", () => {
    const view = reviewView(review);
    expect(commitGuard(view, false)).toBe("protected_path");
    const html = render();
    expect(html).toContain("Diff com path protegido: commit e push bloqueados.");
    expect(html).toContain("Commitar revisão");
    // The confirmation is disabled, so the primary action cannot be armed.
    expect(html).toMatch(/data-commit-guard="protected_path"/);
    expect(html).toContain("disabled");
  });

  it("blocks the commit on a truncated or empty review", () => {
    expect(commitGuard(reviewView(cleanReview), true)).toBe("truncated");
    expect(commitGuard(reviewView({ ...cleanReview, diff: "" }), false)).toBe("no_changes");
    expect(commitGuard(reviewView(cleanReview), false)).toBeNull();
    expect(commitGuardLabel(null)).toContain("Commit disponível");
    expect(render({ review: { ...review, truncated: true } })).toContain("Diff truncado: commit bloqueado.");
  });

  it("requires a message and an explicit confirmation before committing", () => {
    expect(commitMessageError("   ")).toBe("review_message_empty");
    expect(commitMessageError("a".repeat(4_097))).toBe("review_message_too_large");
    expect(commitMessageError("  feat: x  ")).toBeNull();
    const html = render({ review: cleanReview, commitConfirmed: false, commitMessage: "   " });
    expect(html).toContain("Confirmo commitar 1 arquivo(s) revisado(s)");
    expect(html).toContain("Commit disponível para os arquivos revisados.");
    expect(html).toContain("Escreva a mensagem do commit.");
    const ready = render({ review: cleanReview, commitMessage: "feat: x" });
    expect(ready).not.toContain("Escreva a mensagem do commit.");
  });

  it("shows the commit sha and the receipt after a commit", () => {
    const html = render({ review: cleanReview, commitReceipt });
    expect(html).toContain("Commit <code>" + sha + "</code>");
    expect(html).toContain(".simplicio/review-commits/");
    expect(html).toContain("Ainda não há push registrado para este commit.");
    expect(html).toContain("Recarregue o diff para revisar o próximo estado da worktree.");
    // The message itself is never echoed back as stored data.
    expect(html).toContain("A mensagem não é gravada no recibo, apenas o digest");
  });

  it("shows the real stderr when the commit hook fails", () => {
    const html = render({ review: cleanReview, commitReceipt: failedCommit });
    expect(html).toContain('data-testid="review-commit-stderr"');
    expect(html).toContain("pre-commit: lint failed on a.txt");
    expect(html).toContain("O commit não foi criado (review_commit_failed)");
    expect(html).not.toContain("Ainda não há push registrado");
  });

  it("shows the real stderr when the push is rejected", () => {
    const html = render({ review: cleanReview, commitReceipt, pushReceipt: failedPush });
    expect(html).toContain('data-testid="review-push-stderr"');
    expect(html).toContain("non-fast-forward");
    expect(html).toContain("O push foi recusado (review_push_failed)");
  });

  it("accepts a pushed receipt and keeps the upstream visible", () => {
    const html = render({
      review: cleanReview,
      commitReceipt,
      pushReceipt: { ...failedPush, status: "pushed", code: null, stderr: null, upstream: "origin/issue-469" },
    });
    expect(html).toContain("Push concluído em <code>origin/issue-469</code>");
  });

  it("parses the native commit and push receipts and rejects dishonest ones", () => {
    expect(parseReviewCommitReceipt(commitReceipt).sha).toBe(sha);
    expect(parseReviewCommitReceipt(failedCommit).stderr).toContain("lint failed");
    // A "committed" receipt without a sha or a path is refused.
    expect(() => parseReviewCommitReceipt({ ...commitReceipt, sha: null })).toThrow("review_commit_receipt_invalid");
    expect(() => parseReviewCommitReceipt({ ...commitReceipt, path: null })).toThrow("review_commit_receipt_invalid");
    expect(() => parseReviewCommitReceipt({ ...commitReceipt, sha: "zzz" })).toThrow("review_commit_receipt_invalid");
    expect(() => parseReviewCommitReceipt({ ...commitReceipt, status: "ok" })).toThrow("review_commit_receipt_invalid");
    expect(() => parseReviewCommitReceipt({ ...commitReceipt, redacted: false })).toThrow("review_commit_receipt_invalid");

    expect(parseReviewPushReceipt({ ...failedPush, status: "pushed", upstream: "origin/issue-469" }).upstream).toBe("origin/issue-469");
    // A successful push without an upstream is not a receipt.
    expect(() => parseReviewPushReceipt({ ...failedPush, status: "pushed", upstream: null })).toThrow("review_push_receipt_invalid");
    expect(() => parseReviewPushReceipt({ ...failedPush, sha: "short" })).toThrow("review_push_receipt_invalid");
  });
});
