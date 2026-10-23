import { describe, expect, it } from "vitest";
import {
  DEFAULT_TRACK_WIP,
  FLEET_QUEUE_SCHEMA,
  admitFleetTask,
  emptyFleetQueue,
  fleetQueueErrorMessage,
  normalizeFleetTask,
  parseFleetQueue,
  projectFleetQueue,
  trackActiveWip,
  upsertFleetTask,
  type FleetQueue,
  type FleetTask,
  type FleetTaskDraft,
} from "./fleet_queue";

const STAMP = "2026-10-23T12:00:00.000Z";

function draft(overrides: Partial<FleetTaskDraft> & Pick<FleetTaskDraft, "id">): FleetTaskDraft {
  return {
    issue: 433,
    worktree: "C:/wt/issue-433",
    agent: "claude",
    track: "desktop",
    wave: 1,
    status: "queued",
    parent: null,
    updated_at: STAMP,
    ...overrides,
  };
}

function task(overrides: Partial<FleetTask> & Pick<FleetTask, "id">): FleetTask {
  return normalizeFleetTask(draft(overrides));
}

function queue(tasks: FleetTask[], wip: Record<string, number> = {}): FleetQueue {
  return { schema: FLEET_QUEUE_SCHEMA, wip_per_track: wip, tasks };
}

describe("fleet queue contract", () => {
  it("parses a persisted queue and rejects drift", () => {
    const parsed = parseFleetQueue({
      schema: FLEET_QUEUE_SCHEMA,
      wip_per_track: { desktop: 2 },
      tasks: [draft({ id: "433-desktop", issue: 433, lane: "queued" })],
    });
    expect(parsed.tasks).toHaveLength(1);
    expect(parsed.tasks[0].lane).toBe("queued");
    expect(parsed.wip_per_track.desktop).toBe(2);

    expect(() => parseFleetQueue({ schema: "other", tasks: [] })).toThrow("fleet_queue_invalid");
    expect(() => parseFleetQueue({ schema: FLEET_QUEUE_SCHEMA, tasks: [{ ...draft({ id: "x" }), status: "paused" }] })).toThrow("status_invalid");
    expect(() => parseFleetQueue({ schema: FLEET_QUEUE_SCHEMA, tasks: [{ ...draft({ id: "x" }), status: "running", lane: "queued" }] })).toThrow("lane_status_mismatch");
    expect(() => parseFleetQueue({ schema: FLEET_QUEUE_SCHEMA, tasks: [{ ...draft({ id: "x" }), updated_at: "yesterday" }] })).toThrow("updated_at_invalid");
  });

  it("never invents orientation measurements", () => {
    const unmeasured = task({ id: "433-desktop" });
    expect(unmeasured.orientation_ms).toBeUndefined();
    expect(unmeasured.started_at).toBeUndefined();

    const measured = task({ id: "434-desktop", orientation_ms: 1400, started_at: STAMP });
    expect(measured.orientation_ms).toBe(1400);
    expect(measured.started_at).toBe(STAMP);

    expect(() => task({ id: "bad", orientation_ms: -1 })).toThrow("orientation_invalid");
    expect(projectFleetQueue(queue([unmeasured])).orientation).toEqual({ measured: 0, unmeasured: 1, median_ms: null });
    expect(projectFleetQueue(queue([measured, unmeasured])).orientation).toEqual({ measured: 1, unmeasured: 1, median_ms: 1400 });
  });
});

describe("fleet queue projection", () => {
  const tasks = [
    task({ id: "433-desktop", wave: 1, status: "running", track: "desktop" }),
    task({ id: "433-runtime", wave: 1, status: "queued", track: "runtime" }),
    task({ id: "434-desktop", wave: 2, status: "needs_review", track: "desktop", parent: "433-desktop" }),
    task({ id: "435-desktop", wave: 2, status: "done", track: "desktop", parent: "433-desktop" }),
  ];

  it("builds deterministic lanes, tracks, waves and WIP", () => {
    const board = projectFleetQueue(queue(tasks, { desktop: 2 }));
    expect(board.lanes.map((lane) => lane.name)).toEqual(["queued", "running", "blocked", "needs_review", "done"]);
    expect(board.lanes[0].tasks.map((item) => item.id)).toEqual(["433-runtime"]);
    expect(board.tracks.map((item) => item.name)).toEqual(["desktop", "runtime"]);
    expect(board.tracks[0]).toMatchObject({ activeWip: 2, limit: 2, atLimit: true, overLimit: false });
    expect(board.tracks[1]).toMatchObject({ activeWip: 1, limit: DEFAULT_TRACK_WIP, atLimit: false });
    expect(board.waves.map((wave) => wave.wave)).toEqual([1, 2]);
    expect(board.waves[0].tracks).toEqual(["desktop", "runtime"]);
    expect(board.counts).toMatchObject({ total: 4, active: 3, queued: 1, running: 1, needs_review: 1, done: 1 });
  });

  it("nests parent and child tasks once and deterministically", () => {
    const board = projectFleetQueue(queue(tasks));
    expect(board.roots).toHaveLength(2);
    const root = board.roots.find((node) => node.task.id === "433-desktop");
    expect(root?.children.map((node) => node.task.id)).toEqual(["434-desktop", "435-desktop"]);

    const shuffled = projectFleetQueue(queue([...tasks].reverse()));
    expect(JSON.stringify(shuffled)).toBe(JSON.stringify(board));
  });
});

describe("fleet queue admission", () => {
  const current = queue(
    [
      task({ id: "433-desktop", status: "running", track: "desktop" }),
      task({ id: "434-desktop", status: "running", track: "desktop" }),
      task({ id: "435-desktop", status: "done", track: "desktop" }),
    ],
    { desktop: 2 },
  );

  it("enforces WIP per track before admitting another task", () => {
    const rejected = admitFleetTask(current, draft({ id: "436-desktop" }));
    expect(rejected.ok).toBe(false);
    if (rejected.ok) throw new Error("expected rejection");
    expect(rejected.error).toBe("wip_limit_reached:desktop");
    expect(rejected).toMatchObject({ track: "desktop", active: 2, limit: 2 });
    expect(fleetQueueErrorMessage(rejected.error)).toContain('track "desktop"');
    expect(fleetQueueErrorMessage(rejected.error)).toContain("Mova uma tarefa para done");

    const blockedByQueue = admitFleetTask(current, draft({ id: "437-desktop", status: "blocked" }));
    expect(blockedByQueue.ok).toBe(false);

    const done = admitFleetTask(current, draft({ id: "438-desktop", status: "done" }));
    expect(done.ok).toBe(true);

    const otherTrack = admitFleetTask(current, draft({ id: "439-runtime", track: "runtime" }));
    expect(otherTrack.ok).toBe(true);
  });

  it("does not count the task being updated against itself", () => {
    const promoted = admitFleetTask(current, draft({ id: "433-desktop", status: "running" }));
    expect(promoted.ok).toBe(true);
    expect(trackActiveWip(current, "desktop", "433-desktop")).toBe(1);

    const limitChange = admitFleetTask(current, draft({ id: "440-desktop" }), { desktop: 3 });
    expect(limitChange.ok).toBe(true);
  });

  it("rejects unknown parents and cycles", () => {
    const unknown = admitFleetTask(current, draft({ id: "441-desktop", parent: "missing" }));
    expect(unknown.ok).toBe(false);
    if (!unknown.ok) expect(unknown.error).toBe("parent_unknown:missing");

    const chained = queue([
      task({ id: "a", parent: null }),
      task({ id: "b", parent: "a" }),
    ]);
    const cycle = admitFleetTask(chained, draft({ id: "a", parent: "b" }));
    expect(cycle.ok).toBe(false);
    if (!cycle.ok) expect(cycle.error).toBe("task_cycle");
  });
});

describe("fleet queue upsert", () => {
  it("is idempotent for the same task and updated_at", () => {
    const base = emptyFleetQueue({ desktop: 2 });
    const first = upsertFleetTask(base, draft({ id: "433-desktop", parent: null }));
    const second = upsertFleetTask(first, draft({ id: "433-desktop", parent: null }));
    expect(JSON.stringify(second)).toBe(JSON.stringify(first));
    expect(first.tasks).toHaveLength(1);

    const updated = upsertFleetTask(second, draft({ id: "433-desktop", status: "running" }));
    expect(updated.tasks).toHaveLength(1);
    expect(updated.tasks[0].status).toBe("running");
    expect(updated.tasks[0].lane).toBe("running");
  });

  it("sorts tasks deterministically regardless of insertion order", () => {
    const a = task({ id: "b", wave: 2, track: "desktop" });
    const b = task({ id: "a", wave: 1, track: "runtime" });
    const c = task({ id: "c", wave: 1, track: "desktop" });
    const left = upsertFleetTask(upsertFleetTask(upsertFleetTask(emptyFleetQueue(), a), b), c);
    const right = upsertFleetTask(upsertFleetTask(upsertFleetTask(emptyFleetQueue(), c), a), b);
    expect(left.tasks.map((item) => item.id)).toEqual(["c", "a", "b"]);
    expect(JSON.stringify(left)).toBe(JSON.stringify(right));
  });

  it("defaults a missing lane to the status and stamps only when asked", () => {
    const stamped = normalizeFleetTask({ ...draft({ id: "433-desktop" }), updated_at: undefined });
    expect(stamped.lane).toBe(stamped.status);
    expect(stamped.updated_at).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    expect(() => normalizeFleetTask({ ...draft({ id: "433-desktop" }), updated_at: undefined }, { stamp: false })).toThrow("updated_at_invalid");
  });
});
