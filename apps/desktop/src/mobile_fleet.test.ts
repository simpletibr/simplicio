import { describe, expect, it } from "vitest";
import mobileCss from "./mobile_fleet.css?raw";
import {
  MOBILE_FLEET_MAX_WIDTH,
  MOBILE_FLEET_TESTED_WIDTHS,
  buildMobileFleet,
  fleetLayoutMode,
  receiptOwner,
} from "./mobile_fleet";
import {
  REMOTE_FLEET_SCHEMA,
  parseRemoteFleet,
  parseRemoteWorkers,
  type RemoteFleet,
  type RemoteMachine,
  type RemoteWorker,
} from "./remote_fleet";

/** The sheet is read verbatim: the CSS contract is part of the layout test. */
const mobileCssText: string = mobileCss;

function worker(overrides: Partial<RemoteWorker> = {}): RemoteWorker {
  return {
    id: "w-1",
    label: "issue-468",
    claim: "issue:468",
    state: "running",
    progress: { done: 3, total: 7 },
    receiptId: "rcpt-468-1",
    ...overrides,
  };
}

function machine(overrides: Partial<RemoteMachine> = {}): RemoteMachine {
  return {
    id: "mac-mini",
    label: "Mac mini",
    url: "http://127.0.0.1:8787",
    status: "online",
    authenticated: true,
    version: "3.10.0",
    latencyMs: 18,
    reasonCode: null,
    workers: [worker()],
    ...overrides,
  };
}

function fleet(remotes: RemoteMachine[]): RemoteFleet {
  return parseRemoteFleet({
    schema: REMOTE_FLEET_SCHEMA,
    configured: true,
    redacted: true,
    observedAt: 1_900_000_000,
    error: null,
    remotes,
  });
}

describe("mobile fleet layout boundary", () => {
  it("treats <= 480 px as the read-mostly mobile layout and 481 px as the panel", () => {
    for (const width of MOBILE_FLEET_TESTED_WIDTHS) {
      expect(fleetLayoutMode(width)).toBe("mobile");
    }
    expect(fleetLayoutMode(320)).toBe("mobile");
    expect(fleetLayoutMode(MOBILE_FLEET_MAX_WIDTH)).toBe("mobile");
    expect(fleetLayoutMode(MOBILE_FLEET_MAX_WIDTH + 1)).toBe("wide");
    expect(fleetLayoutMode(1_024)).toBe("wide");
    // A non-measured viewport never claims the mobile layout.
    expect(fleetLayoutMode(0)).toBe("wide");
    expect(fleetLayoutMode(Number.NaN)).toBe("wide");
    expect(fleetLayoutMode(Number.POSITIVE_INFINITY)).toBe("wide");
  });

  it("pins the CSS contract that removes horizontal scroll", () => {
    // The breakpoint is declared once, at the documented width.
    expect(mobileCssText).toContain(`@media (max-width: ${MOBILE_FLEET_MAX_WIDTH}px)`);
    // Every grid track of the narrow layout may shrink below its content.
    expect(mobileCssText).toContain("grid-template-columns: minmax(0, 1fr)");
    expect(mobileCssText).toContain("min-width: 0");
    expect(mobileCssText).toContain("max-width: 100%");
    // Long urls, ids, claims and receipts wrap instead of pushing the page.
    expect(mobileCssText).toContain("overflow-wrap: anywhere");
    expect(mobileCssText).not.toContain("nowrap");
    // No element in this sheet requests a fixed width wider than the viewport.
    const fixedWidths = [...mobileCssText.matchAll(/(?<![-a-z])width:\s*(\d+)px/g)].map((match) => Number(match[1]));
    expect(fixedWidths.every((width) => width <= MOBILE_FLEET_MAX_WIDTH)).toBe(true);
  });
});

describe("mobile fleet projection", () => {
  const value = fleet([
    machine({}),
    machine({
      id: "studio",
      label: "Studio",
      url: "https://studio.example.test/a/very/long/path/that/must/wrap",
      status: "offline",
      authenticated: false,
      version: null,
      latencyMs: null,
      reasonCode: "remote_unreachable",
      workers: [worker({ id: "w-9", label: "review", claim: null, state: "blocked", progress: null, receiptId: null })],
    }),
  ]);

  it("carries machines, workers, claims, progress and receipts at 375 and 480 px", () => {
    for (const width of MOBILE_FLEET_TESTED_WIDTHS) {
      const projection = buildMobileFleet(value, width);
      expect(projection.schema).toBe("simplicio.desktop-mobile-fleet/v1");
      expect(projection.layout).toBe("mobile");
      expect(projection.width).toBe(width);
      expect(projection.reasonCode).toBe("mobile_fleet_ready");
      expect(projection.summary).toEqual({
        machines: 2,
        actionable: 1,
        workers: 2,
        running: 1,
        paused: 0,
        blocked: 1,
        withReceipt: 1,
      });

      const [mac, studio] = projection.machines;
      expect(mac.statusLabel).toBe("Online");
      expect(mac.versionLabel).toBe("versão 3.10.0");
      expect(mac.latencyLabel).toBe("18 ms");
      expect(mac.workers[0].claimLabel).toBe("issue:468");
      expect(mac.workers[0].stateLabel).toBe("Em execução");
      expect(mac.workers[0].progressLabel).toBe("3/7 passo(s)");
      expect(mac.workers[0].receiptId).toBe("rcpt-468-1");
      expect(mac.receipts).toEqual(["rcpt-468-1"]);

      expect(studio.workers[0].claimLabel).toBe("sem claim reportado");
      expect(studio.workers[0].progressLabel).toBe("progresso não informado");
    }
  });

  it("hides the steering controls unless the machine is online and authenticated", () => {
    const projection = buildMobileFleet(value, 375);
    const [mac, studio] = projection.machines;

    // Online + token accepted: the two allowed actions are projected.
    expect(mac.actionable).toBe(true);
    expect(mac.workers[0].steer.map((view) => view.action)).toEqual(["pause", "resume"]);
    expect(mac.workers[0].steer[0].enabled).toBe(true);
    // Resume is disabled, with a visible reason, while the worker runs.
    expect(mac.workers[0].steer[1].enabled).toBe(false);
    expect(mac.workers[0].steer[1].blocker).toContain("pausado");
    expect(mac.workers[0].hiddenReason).toBeNull();

    // Offline: no control is rendered at all, and the reason is explicit.
    expect(studio.actionable).toBe(false);
    expect(studio.workers[0].steer).toEqual([]);
    expect(studio.workers[0].hiddenReason).toContain("offline");
    expect(studio.blocker).toContain("offline");

    // A finished worker exposes no steering action at all.
    expect(buildMobileFleet(fleet([machine({ workers: [worker({ state: "done" })] })]), 375).machines[0].workers[0].steer.map((view) => view.enabled))
      .toEqual([false, false]);
  });

  it("offers resume only for a paused worker", () => {
    const projection = buildMobileFleet(fleet([machine({ workers: [worker({ state: "paused" })] })]), 480);
    const steer = projection.machines[0].workers[0].steer;
    expect(steer.map((view) => [view.action, view.enabled])).toEqual([
      ["pause", false],
      ["resume", true],
    ]);
    expect(steer[0].blocker).toContain("em execução");
  });

  it("never invents a worker, a progress number or a receipt", () => {
    const empty = buildMobileFleet(fleet([machine({ workers: [] })]), 375);
    expect(empty.machines[0].workers).toEqual([]);
    expect(empty.machines[0].workersReason).toContain("Nenhum worker reportado");
    expect(empty.machines[0].receipts).toEqual([]);
    expect(empty.summary.workers).toBe(0);

    const unknown = buildMobileFleet(null, 375);
    expect(unknown.reasonCode).toBe("mobile_fleet_unavailable");
    expect(unknown.machines).toEqual([]);
    expect(unknown.summary.machines).toBe(0);

    const emptyFleet = buildMobileFleet(fleet([]), 375);
    expect(emptyFleet.reasonCode).toBe("mobile_fleet_empty");
  });

  it("recognizes the same receipt the fleet already reports", () => {
    const projection = buildMobileFleet(value, 375);
    expect(receiptOwner(projection, "rcpt-468-1")).toEqual({ machineId: "mac-mini", workerId: "w-1" });
    expect(receiptOwner(projection, "rcpt-from-nowhere")).toBeNull();
  });
});

describe("worker contract parsing", () => {
  it("accepts the bounded worker list and rejects rows that break it", () => {
    expect(parseRemoteWorkers(undefined)).toEqual([]);
    expect(parseRemoteWorkers([worker()])).toHaveLength(1);
    expect(() => parseRemoteWorkers([worker(), worker()])).toThrow("remote_fleet_worker_duplicate");
    expect(() => parseRemoteWorkers([worker({ state: "working" as never })])).toThrow(
      "remote_fleet_worker_state_invalid",
    );
    expect(() => parseRemoteWorkers([worker({ progress: { done: 5, total: 2 } })])).toThrow(
      "remote_fleet_worker_progress_invalid",
    );
    expect(() => parseRemoteWorkers([{ ...worker(), token: "secret" }])).toThrow(
      "remote_fleet_worker_unknown_field",
    );
    expect(() => parseRemoteWorkers([worker({ receiptId: "rcpt with space" })])).toThrow(
      "remote_fleet_worker_receipt_invalid",
    );
    expect(() => parseRemoteWorkers(Array.from({ length: 33 }, (_, index) => worker({ id: `w-${index}` })))).toThrow(
      "remote_fleet_worker_limit",
    );
  });

  it("rejects a worker whose id cannot be addressed in a URL path", () => {
    expect(() => parseRemoteWorkers([worker({ id: "../admin" })])).toThrow("remote_fleet_worker_invalid");
  });
});
