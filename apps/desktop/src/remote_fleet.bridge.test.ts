import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const invokeMock = vi.fn();

// The Tauri command is the only thing mocked: `invoke` delegates to the
// internals object, so no network or native process is involved.
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

describe("desktop_remote_fleet bridge", () => {
  it("requests only the bounded fleet command and parses its projection", async () => {
    invokeMock.mockResolvedValue({
      schema: "simplicio.desktop-remote-fleet/v1",
      configured: true,
      redacted: true,
      observedAt: 1_900_000_000,
      error: null,
      remotes: [
        {
          id: "studio",
          label: "Studio",
          url: "https://studio.example.test",
          status: "online",
          authenticated: true,
          version: "3.10.0",
          latencyMs: 31,
          reasonCode: null,
        },
      ],
    });
    const bridge = await import("./bridge");
    const fleet = await bridge.loadDesktopRemoteFleet();
    expect(invokeMock).toHaveBeenCalledTimes(1);
    expect(invokeMock.mock.calls[0][0]).toBe("desktop_remote_fleet");
    expect(fleet.remotes[0]).toMatchObject({ id: "studio", status: "online", authenticated: true });
    expect(JSON.stringify(fleet)).not.toContain("Bearer");
  });

  it("fails closed in the preview instead of fabricating a fleet", async () => {
    vi.stubGlobal("window", {});
    const bridge = await import("./bridge");
    await expect(bridge.loadDesktopRemoteFleet()).rejects.toThrow("preview_no_runtime");
    expect(invokeMock).not.toHaveBeenCalled();
  });
});
