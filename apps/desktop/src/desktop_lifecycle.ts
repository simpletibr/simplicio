export type DesktopLifecycleEvent = "wake" | "reopen";

export function createDesktopLifecycleSupervisor(
  refreshSnapshot: () => Promise<void>,
  finalizeIdleSessions: () => Promise<void>,
) {
  let inFlight: Promise<void> | null = null;

  async function reconcile(_event: DesktopLifecycleEvent): Promise<void> {
    if (inFlight) return inFlight;
    inFlight = (async () => {
      await refreshSnapshot();
      await finalizeIdleSessions();
    })().finally(() => {
      inFlight = null;
    });
    return inFlight;
  }

  return { reconcile };
}
