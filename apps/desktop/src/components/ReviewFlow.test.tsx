import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ReviewFlowCard } from "./ReviewFlow";
import { parseUnifiedDiff, reviewFlags, reviewView } from "../review";

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

const review = {
  schema: "simplicio.desktop-review/v1" as const,
  repo: "C:/repo",
  base: null,
  status: "",
  diff,
  digest: "sha256:" + "a".repeat(64),
  truncated: false,
};

describe("ReviewFlow", () => {
  it("parses files, flags protected paths and never claims auto-merge without a plan", () => {
    const files = parseUnifiedDiff(diff);
    expect(files.map((file) => file.path)).toEqual(["src/a.ts", "install.sh"]);
    expect(files[0].additions).toBe(2);
    expect(reviewFlags(files)).toEqual([{ path: "install.sh", kind: "protected" }]);
    const view = reviewView(review);
    expect(view.autoMerge.eligible).toBe(false);
    expect(view.autoMerge.reason).toBe("protected_path");
    const html = renderToStaticMarkup(<ReviewFlowCard review={review} comments="fix this" busy={false} onComments={() => undefined} onCopy={() => undefined} />);
    expect(html).toContain("install.sh");
    expect(html).toContain("protected");
    expect(html).toContain("auto-merge");
  });
});
