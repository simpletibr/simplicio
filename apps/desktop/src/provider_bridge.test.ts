import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const { invokeMock } = vi.hoisted(() => ({ invokeMock: vi.fn() }));
vi.mock("@tauri-apps/api/core", () => ({ invoke: invokeMock }));

beforeEach(() => {
  vi.resetModules();
  vi.stubGlobal("window", { __TAURI_INTERNALS__: {} });
  invokeMock.mockReset();
});
afterEach(() => { vi.unstubAllGlobals(); });

describe("provider and request native boundary", () => {
  it("binds only the redacted authoritative provider-session contract", async () => {
    invokeMock.mockResolvedValueOnce({
      schema: "simplicio.desktop-provider-session-binding/v1",
      bound: true,
      runtime_session_id: "runtime-session-1",
      provider: "claude",
      session_id: "runtime-session-1",
      redacted: true,
    });
    const bridge = await import("./bridge");

    await expect(bridge.bindDesktopProviderSession({
      runtimeSessionId: "runtime-session-1",
      provider: "claude-code",
      providerSessionId: "provider-session-1",
      profileId: "profile-1",
      workspaceId: "workspace-1",
    })).resolves.toMatchObject({
      bound: true,
      provider: "claude",
      sessionId: "runtime-session-1",
    });
    expect(invokeMock).toHaveBeenCalledWith("desktop_bind_provider_session", {
      runtimeSessionId: "runtime-session-1",
      provider: "claude",
      providerSessionId: "provider-session-1",
      profileId: "profile-1",
      workspaceId: "workspace-1",
    });
  });

  it("starts and completes durable requests without provider-process control", async () => {
    invokeMock
      .mockResolvedValueOnce({
        schema: "simplicio.desktop-request/v1",
        request_id: "request-1",
        started: true,
        completed: false,
        redacted: true,
      })
      .mockResolvedValueOnce({
        schema: "simplicio.desktop-request/v1",
        request_id: "request-1",
        started: false,
        completed: true,
        redacted: true,
      });
    const bridge = await import("./bridge");

    await expect(bridge.beginDesktopRequest("runtime-session-1", "request-1")).resolves.toBe(true);
    await expect(bridge.completeDesktopRequest("request-1")).resolves.toBe(true);
    expect(invokeMock.mock.calls.map(([command]) => command)).toEqual([
      "desktop_request_start",
      "desktop_request_finish",
    ]);
  });
});
