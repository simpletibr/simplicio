import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { FleetCockpitList } from "./FleetCockpit";
import { fleetState, parseWorktrees } from "../fleet";

const porcelain = [
  "worktree C:/repo",
  "HEAD aaa",
  "branch refs/heads/main",
  "",
  "worktree C:/wt/issue-1",
  "HEAD bbb",
  "branch refs/heads/issue-1",
  "",
  "worktree C:/wt/issue-2",
  "HEAD ccc",
  "branch refs/heads/issue-2",
].join("\n");

const worktrees = parseWorktrees(porcelain);

const noop = () => undefined;

describe("FleetCockpitList", () => {
  it("shows worktrees, issue mapping and WIP enforcement", () => {
    const html = renderToStaticMarkup(
      <FleetCockpitList worktrees={worktrees} repoPath="C:/repo" issue="3" agent="claude" wipLimit={2} busy={false} onRepo={noop} onIssue={noop} onAgent={noop} onWipLimit={noop} onCreate={noop} onRemove={noop} />,
    );
    expect(html).toContain("issue-1");
    expect(html).toContain("issue #1");
    expect(html).toContain("WIP limit atingido");
    expect(html).toContain("Remover");
  });

  it("parses porcelain and computes WIP", () => {
    expect(worktrees[0].main).toBe(true);
    expect(worktrees[1].issue).toBe(1);
    const state = fleetState(worktrees, 2);
    expect(state.active).toBe(2);
    expect(state.overLimit).toBe(true);
  });
});
