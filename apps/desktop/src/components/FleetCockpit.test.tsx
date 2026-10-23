import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { FleetCockpitList } from "./FleetCockpit";
import { fleetState, parseWorktrees } from "../fleet";
import { FLEET_QUEUE_SCHEMA, type FleetQueue } from "../fleet_queue";

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

const queue: FleetQueue = {
  schema: FLEET_QUEUE_SCHEMA,
  wip_per_track: { desktop: 2 },
  tasks: [
    {
      id: "1-desktop",
      issue: 1,
      worktree: "C:/wt/issue-1",
      agent: "claude",
      track: "desktop",
      lane: "running",
      wave: 1,
      status: "running",
      parent: null,
      updated_at: "2026-10-23T12:00:00.000Z",
    },
    {
      id: "2-desktop",
      issue: 2,
      worktree: "C:/wt/issue-2",
      agent: "codex",
      track: "desktop",
      lane: "needs_review",
      wave: 1,
      status: "needs_review",
      parent: "1-desktop",
      updated_at: "2026-10-23T12:00:00.000Z",
      orientation_ms: 1200,
    },
  ],
};

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

  it("renders the queue board with lanes, track WIP, parent link and only measured orientation", () => {
    const html = renderToStaticMarkup(
      <FleetCockpitList
        worktrees={worktrees}
        repoPath="C:/repo"
        issue="3"
        agent="claude"
        wipLimit={2}
        busy={false}
        queue={queue}
        onRepo={noop}
        onIssue={noop}
        onAgent={noop}
        onWipLimit={noop}
        onCreate={noop}
        onRemove={noop}
        onQueueTask={noop}
        onQueueStatus={noop}
      />,
    );
    expect(html).toContain("Fila da fleet");
    expect(html).toContain('data-lane="queued"');
    expect(html).toContain('data-lane="needs_review"');
    expect(html).toContain("desktop · 2/2 WIP");
    expect(html).toContain("filho de 1-desktop");
    expect(html).toContain("1200 ms");
    expect(html).toContain("orientação não medida");
    expect(html).toContain("Wave 1");
    expect(html).toContain("Adicionar à fila");
  });
});
