import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const invokeMock = vi.fn();

// Only the Tauri IPC is mocked: the native command, the HTTP call to the
// remote and the Runtime receipt are outside this bridge test.
beforeEach(() => {
  vi.resetModules();
  vi.stubGlobal("window", {
    __TAURI_INTERNALS__: { invoke: invokeMock },
    setTimeout,
    clearTimeout,
  });
  invokeMock.mockReset();
});
afterEach(() => vi.unstubAllGlobals());

function steerDocument(overrides: Record<string, unknown> = {}) {
  return {
    schema: "simplicio.desktop-fleet-steer/v1",
    machineId: "mac-mini",
    workerId: "w-1",
    action: "pause",
    receiptId: "rcpt-468-1",
    status: "sent",
    latencyMs: 21,
    ...overrides,
  };
}

describe("desktop_fleet_steer bridge", () => {
  it("sends only machine, worker and action, and keeps the runtime receipt", async () => {
    invokeMock.mockResolvedValue(steerDocument());
    const bridge = await import("./bridge");
    const receipt = await bridge.steerRemoteWorker("mac-mini", "w-1", "pause");

    expect(invokeMock).toHaveBeenCalledTimes(1);
    expect(invokeMock.mock.calls[0][0]).toBe("desktop_fleet_steer");
    // No token, URL or free-form body may cross the IPC boundary.
    expect(invokeMock.mock.calls[0][1]).toEqual({
      machineId: "mac-mini",
      workerId: "w-1",
      action: "pause",
    });
    expect(receipt.receiptId).toBe("rcpt-468-1");
    expect(receipt.action).toBe("pause");
  });

  it("surfaces an unauthenticated steer as rejected, without a receipt", async () => {
    invokeMock.mockRejectedValue(new Error("fleet_steer_unauthorized"));
    const bridge = await import("./bridge");
    await expect(bridge.steerRemoteWorker("mac-mini", "w-1", "pause")).rejects.toThrow(
      "fleet_steer_unauthorized",
    );
    expect(invokeMock).toHaveBeenCalledTimes(1);
  });

  it("refuses a 2xx answer that carries no receipt", async () => {
    invokeMock.mockResolvedValue(steerDocument({ receiptId: null }));
    const bridge = await import("./bridge");
    await expect(bridge.steerRemoteWorker("mac-mini", "w-1", "pause")).rejects.toThrow(
      "fleet_steer_receipt_missing",
    );
  });

  it("refuses an answer for another worker or another action", async () => {
    const bridge = await import("./bridge");
    invokeMock.mockResolvedValue(steerDocument({ workerId: "w-2" }));
    await expect(bridge.steerRemoteWorker("mac-mini", "w-1", "pause")).rejects.toThrow(
      "fleet_steer_response_mismatch",
    );
    invokeMock.mockResolvedValue(steerDocument({ action: "resume" }));
    await expect(bridge.steerRemoteWorker("mac-mini", "w-1", "pause")).rejects.toThrow(
      "fleet_steer_response_mismatch",
    );
  });

  it("fails closed in the preview instead of simulating a remote action", async () => {
    vi.stubGlobal("window", {});
    const bridge = await import("./bridge");
    await expect(bridge.steerRemoteWorker("mac-mini", "w-1", "pause")).rejects.toThrow(
      "preview_no_runtime",
    );
    expect(invokeMock).not.toHaveBeenCalled();
  });
});
