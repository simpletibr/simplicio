import { describe, expect, it } from "vitest";
import {
  MAX_REMOTE_FLEET,
  REMOTE_CONFIG_SCHEMA,
  REMOTE_FLEET_SCHEMA,
  REMOTE_STEER_SCHEMA,
  canActOnRemote,
  canSteerWorker,
  classifyRemoteHealth,
  normalizeRemoteUrl,
  parseRemoteConfig,
  parseRemoteFleet,
  parseSteerReceipt,
  redactRemoteText,
  remoteActionBlocker,
  remoteFleetErrorMessage,
  summarizeRemoteFleet,
  summarizeRemoteWorkers,
  workerSteerActions,
  workerSteerBlocker,
  type RemoteMachine,
  type RemoteWorker,
} from "./remote_fleet";

function config(remotes: unknown[]) {
  return { schema: REMOTE_CONFIG_SCHEMA, remotes };
}

function machine(overrides: Partial<RemoteMachine> = {}): RemoteMachine {
  return {
    id: "mac-mini",
    label: "Mac mini",
    url: "http://127.0.0.1:8787",
    status: "online",
    authenticated: true,
    version: "3.10.0",
    latencyMs: 12,
    reasonCode: null,
    ...overrides,
  };
}

function fleet(remotes: unknown[], extra: Record<string, unknown> = {}) {
  return {
    schema: REMOTE_FLEET_SCHEMA,
    configured: true,
    redacted: true,
    observedAt: 1_900_000_000,
    error: null,
    remotes,
    ...extra,
  };
}

describe("simplicio.desktop-remotes/v1", () => {
  it("accepts loopback without a token and requires token_env off loopback", () => {
    const parsed = parseRemoteConfig(
      config([
        { id: "mac-mini", label: " Mac mini ", url: "http://127.0.0.1:8787/" },
        {
          id: "studio",
          label: "Studio",
          url: "https://studio.example.test/",
          token_env: "SIMPLICIO_REMOTE_STUDIO_TOKEN",
        },
      ]),
    );
    expect(parsed.remotes[0].label).toBe("Mac mini");
    expect(parsed.remotes[0].url).toBe("http://127.0.0.1:8787");
    expect(parsed.remotes[0].tokenEnv).toBeNull();
    expect(parsed.remotes[1].tokenEnv).toBe("SIMPLICIO_REMOTE_STUDIO_TOKEN");

    expect(() =>
      parseRemoteConfig(config([{ id: "studio", label: "Studio", url: "https://studio.example.test" }])),
    ).toThrow("remote_config_token_required");
  });

  it("never accepts a literal token or credentials in the file", () => {
    expect(() =>
      parseRemoteConfig(
        config([{ id: "studio", label: "Studio", url: "https://studio.example.test", token: "abc" }]),
      ),
    ).toThrow("remote_config_unknown_field");
    expect(() =>
      parseRemoteConfig(
        config([
          {
            id: "studio",
            label: "Studio",
            url: "https://studio.example.test",
            token_env: "ghp_0123456789abcdefghijklmnop",
          },
        ]),
      ),
    ).toThrow("remote_config_token_env_invalid");
    expect(() =>
      parseRemoteConfig(
        config([
          {
            id: "studio",
            label: "Studio",
            url: "https://user:password@studio.example.test",
            token_env: "SIMPLICIO_REMOTE_STUDIO_TOKEN",
          },
        ]),
      ),
    ).toThrow("remote_config_url_credentials");
    expect(() =>
      parseRemoteConfig(config([{ id: "mini", label: "sk-abcdefghijklmnopqrst", url: "http://127.0.0.1" }])),
    ).toThrow("remote_config_label_invalid");
  });

  it("denies non-http(s) URLs and embedded query or fragment", () => {
    expect(() => normalizeRemoteUrl("ftp://127.0.0.1")).toThrow("remote_config_url_insecure");
    expect(() => normalizeRemoteUrl("http://127.0.0.1:8787/?token=1")).toThrow("remote_config_url_invalid");
    expect(() => normalizeRemoteUrl("http://127.0.0.1:8787/#x")).toThrow("remote_config_url_invalid");
  });

  it("bounds the fleet at 32 unique identifiers", () => {
    const entries = Array.from({ length: MAX_REMOTE_FLEET + 1 }, (_, index) => ({
      id: "remote-" + index,
      label: "Remote",
      url: "http://127.0.0.1:8787",
    }));
    expect(() => parseRemoteConfig(config(entries))).toThrow("remote_config_limit");
    expect(() =>
      parseRemoteConfig(
        config([
          { id: "mini", label: "Mini", url: "http://127.0.0.1:8787" },
          { id: "mini", label: "Mini 2", url: "http://127.0.0.1:8788" },
        ]),
      ),
    ).toThrow("remote_config_duplicate");
    expect(() => parseRemoteConfig({ schema: "other", remotes: [] })).toThrow("remote_config_schema");
  });
});

describe("status mapping", () => {
  it("maps authorization and health responses without inventing success", () => {
    expect(classifyRemoteHealth(200, { status: "ok", version: "3.10.0" }, true)).toEqual({
      status: "online",
      authenticated: true,
      version: "3.10.0",
      reasonCode: null,
    });
    expect(classifyRemoteHealth(200, { status: "ok" }, false)).toEqual({
      status: "online",
      authenticated: false,
      version: null,
      reasonCode: null,
    });
    expect(classifyRemoteHealth(401, {}, true)).toEqual({
      status: "unauthorized",
      authenticated: false,
      version: null,
      reasonCode: "remote_unauthorized",
    });
    expect(classifyRemoteHealth(403, {}, true).status).toBe("unauthorized");
    expect(classifyRemoteHealth(500, {}, true)).toEqual({
      status: "offline",
      authenticated: false,
      version: null,
      reasonCode: "remote_http_error",
    });
    expect(classifyRemoteHealth(200, { status: "degraded" }, true).status).toBe("offline");
    expect(classifyRemoteHealth(200, "not-json", true).status).toBe("offline");
  });

  it("keeps only online and authenticated remotes actionable", () => {
    expect(canActOnRemote(machine())).toBe(true);
    expect(canActOnRemote(machine({ authenticated: false }))).toBe(false);
    expect(canActOnRemote(machine({ status: "offline" }))).toBe(false);
    expect(canActOnRemote(machine({ status: "unauthorized" }))).toBe(false);
    expect(remoteActionBlocker(machine())).toBeNull();
    expect(remoteActionBlocker(machine({ status: "offline" }))).toContain("offline");
    expect(remoteActionBlocker(machine({ status: "unauthorized" }))).toContain("autorização");
    expect(remoteActionBlocker(machine({ authenticated: false }))).toContain("token");
  });

  it("summarizes a bounded fleet", () => {
    const summary = summarizeRemoteFleet([
      machine(),
      machine({ id: "b", status: "offline" }),
      machine({ id: "c", status: "unauthorized", authenticated: false }),
      machine({ id: "d", authenticated: false }),
    ]);
    expect(summary).toEqual({ total: 4, online: 2, offline: 1, unauthorized: 1, actionable: 1 });
  });
});

describe("worker steering contract", () => {
  function worker(overrides: Partial<RemoteWorker> = {}): RemoteWorker {
    return {
      id: "w-1",
      label: "issue-468",
      claim: "issue:468",
      state: "running",
      progress: { done: 1, total: 4 },
      receiptId: "rcpt-1",
      ...overrides,
    };
  }

  it("allows pause for a running worker and resume for a paused one", () => {
    expect(workerSteerActions(worker())).toEqual(["pause"]);
    expect(workerSteerActions(worker({ state: "paused" }))).toEqual(["resume"]);
    expect(workerSteerActions(worker({ state: "done" }))).toEqual([]);
    expect(canSteerWorker(machine(), worker(), "pause")).toBe(true);
    expect(canSteerWorker(machine(), worker(), "resume")).toBe(false);
    expect(canSteerWorker(machine(), worker({ state: "paused" }), "resume")).toBe(true);
    expect(workerSteerBlocker(machine(), worker(), "resume")).toContain("pausado");
  });

  it("requires an online and authenticated machine for any steering action", () => {
    for (const offline of [
      machine({ status: "offline" }),
      machine({ status: "unauthorized", authenticated: false }),
      machine({ authenticated: false }),
      machine({ status: "unknown" }),
    ]) {
      expect(canSteerWorker(offline, worker(), "pause")).toBe(false);
      expect(workerSteerBlocker(offline, worker(), "pause")).not.toBeNull();
    }
  });

  it("parses the native steer receipt and rejects a fabricated one", () => {
    const parsed = parseSteerReceipt(
      {
        schema: REMOTE_STEER_SCHEMA,
        machineId: "mac-mini",
        workerId: "w-1",
        action: "pause",
        receiptId: "rcpt-468-1",
        status: "sent",
      },
      { machineId: "mac-mini", workerId: "w-1", action: "pause" },
    );
    expect(parsed.receiptId).toBe("rcpt-468-1");
    const expected = { machineId: "mac-mini", workerId: "w-1", action: "pause" as const };
    expect(() => parseSteerReceipt({}, expected)).toThrow("fleet_steer_response_schema");
    expect(() =>
      parseSteerReceipt(
        {
          schema: REMOTE_STEER_SCHEMA,
          machineId: "mac-mini",
          workerId: "w-1",
          action: "pause",
          receiptId: "",
          status: "sent",
        },
        expected,
      ),
    ).toThrow("fleet_steer_receipt_missing");
    expect(() =>
      parseSteerReceipt(
        {
          schema: REMOTE_STEER_SCHEMA,
          machineId: "studio",
          workerId: "w-1",
          action: "pause",
          receiptId: "rcpt-1",
          status: "sent",
        },
        expected,
      ),
    ).toThrow("fleet_steer_response_mismatch");
    expect(remoteFleetErrorMessage("fleet_steer_unauthorized")).toContain("não autorizado");
  });

  it("summarizes the workers the remote reported", () => {
    expect(
      summarizeRemoteWorkers([
        machine({ workers: [worker(), worker({ id: "w-2", state: "paused", receiptId: null })] }),
        machine({ id: "studio", workers: [worker({ id: "w-3", state: "blocked" })] }),
      ]),
    ).toEqual({ total: 3, running: 1, paused: 1, blocked: 1, withReceipt: 2 });
    expect(summarizeRemoteWorkers([machine({ workers: [] })])).toEqual({
      total: 0,
      running: 0,
      paused: 0,
      blocked: 0,
      withReceipt: 0,
    });
  });
});

describe("simplicio.desktop-remote-fleet/v1", () => {
  it("parses the native projection and rejects unredacted payloads", () => {
    const parsed = parseRemoteFleet(fleet([machine()]));
    expect(parsed.remotes[0].status).toBe("online");
    expect(parsed.observedAt).toBe(1_900_000_000);
    expect(() => parseRemoteFleet(fleet([machine()], { redacted: false }))).toThrow("remote_fleet_unredacted");
    expect(() => parseRemoteFleet(fleet([machine({ status: "degraded" as never })]))).toThrow(
      "remote_fleet_status_invalid",
    );
    expect(() => parseRemoteFleet(fleet([{ ...machine(), token: "secret" }]))).toThrow(
      "remote_fleet_unknown_field",
    );
    expect(() => parseRemoteFleet(fleet([{ ...machine(), authenticated: "yes" }]))).toThrow(
      "remote_fleet_invalid",
    );
    expect(() =>
      parseRemoteFleet(fleet([machine({ status: "unauthorized", authenticated: true })])),
    ).toThrow("remote_fleet_invalid");
  });

  it("caps the projection and redacts diagnostics", () => {
    const entries = Array.from({ length: MAX_REMOTE_FLEET + 1 }, (_, index) =>
      machine({ id: "remote-" + index }),
    );
    expect(() => parseRemoteFleet(fleet(entries))).toThrow("remote_fleet_limit");

    const message = redactRemoteText(
      "Bearer abc.def.ghi token=supersecret ghp_0123456789abcdefghijklmnop\u0000",
    );
    expect(message).not.toContain("abc.def.ghi");
    expect(message).not.toContain("supersecret");
    expect(message).not.toContain("ghp_0123456789abcdefghijklmnop");
    expect(message).toContain("[redacted]");
    expect(remoteFleetErrorMessage("remote_config_token_required")).toContain("token_env");
    expect(remoteFleetErrorMessage("remote_unreachable")).toContain("Falha");
  });
});
