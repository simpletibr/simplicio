import { beforeEach, describe, expect, it, vi } from "vitest";

const invokeMock = vi.fn();

vi.mock("@tauri-apps/api/core", () => ({
  invoke: (...args: unknown[]) => invokeMock(...args),
}));

const page = {
  schema: "simplicio.desktop-events-page/v1",
  stream_id: "stream-1",
  events: [],
  next_cursor: 0,
  has_more: false,
  head_cursor: 0,
  retention_window: 4096,
};

describe("activity poll budget (#432: an event reaches the screen within 1 s)", () => {
  beforeEach(() => {
    invokeMock.mockReset();
    invokeMock.mockResolvedValue(page);
    vi.stubGlobal("window", {
      __TAURI_INTERNALS__: {},
      setTimeout: globalThis.setTimeout,
      clearTimeout: globalThis.clearTimeout,
    });
  });

  it("keeps the worst-case delivery inside one second", async () => {
    const {
      ACTIVITY_POLL_BUDGET_MS,
      ACTIVITY_POLL_GAP_MS,
      ACTIVITY_POLL_SPAWN_BUDGET_MS,
      ACTIVITY_POLL_WAIT_MS,
    } = await import("./bridge");
    const worstCase = ACTIVITY_POLL_WAIT_MS + ACTIVITY_POLL_GAP_MS + ACTIVITY_POLL_SPAWN_BUDGET_MS;
    expect(ACTIVITY_POLL_BUDGET_MS).toBe(1_000);
    expect(worstCase).toBeLessThanOrEqual(ACTIVITY_POLL_BUDGET_MS);
    // The screen must leave exactly the gap this budget was computed with.
    expect(ACTIVITY_POLL_GAP_MS).toBe(250);
  });

  it("sends the bounded wait to the native command by default", async () => {
    const { ACTIVITY_POLL_WAIT_MS, loadDesktopActivityEvents } = await import("./bridge");
    await loadDesktopActivityEvents(0);
    expect(invokeMock).toHaveBeenCalledWith("desktop_activity_events", {
      afterCursor: 0,
      waitMs: ACTIVITY_POLL_WAIT_MS,
    });
  });

  it("never asks the daemon to block longer than the budget", async () => {
    const { ACTIVITY_POLL_BUDGET_MS, loadDesktopActivityEvents } = await import("./bridge");
    await loadDesktopActivityEvents(7, 60_000);
    expect(invokeMock).toHaveBeenCalledWith("desktop_activity_events", {
      afterCursor: 7,
      waitMs: ACTIVITY_POLL_BUDGET_MS,
    });
  });
});
