import { describe, expect, it, vi } from "vitest";
import { createDesktopLifecycleSupervisor } from "./desktop_lifecycle";

describe("desktop lifecycle recovery", () => {
  it("coalesces wake and reopen into one refresh/finalization acceptance path", async () => {
    let release!: () => void;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const refresh = vi.fn(async () => gate);
    const finalize = vi.fn(async () => undefined);
    const supervisor = createDesktopLifecycleSupervisor(refresh, finalize);

    const wake = supervisor.reconcile("wake");
    const reopen = supervisor.reconcile("reopen");
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(finalize).not.toHaveBeenCalled();

    release();
    await Promise.all([wake, reopen]);
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(finalize).toHaveBeenCalledTimes(1);
  });

  it("runs a later wake after the first recovery completes", async () => {
    const refresh = vi.fn(async () => undefined);
    const finalize = vi.fn(async () => undefined);
    const supervisor = createDesktopLifecycleSupervisor(refresh, finalize);

    await supervisor.reconcile("wake");
    await supervisor.reconcile("reopen");
    expect(refresh).toHaveBeenCalledTimes(2);
    expect(finalize).toHaveBeenCalledTimes(2);
  });
});
