/**
 * Read-mostly projection for a narrow Desktop window (<= 480 px): machines,
 * workers, claims, progress and receipts, plus the single steering action this
 * version allows (pause/resume one worker).
 *
 * The projection only re-arranges the existing `simplicio.desktop-remote-fleet/v1`
 * data produced by `desktop_remote_fleet`. It never fetches on its own, never
 * invites a second fleet query from the mobile layout, and never invents a
 * worker, a progress number or a receipt.
 */
import {
  MAX_REMOTE_FLEET,
  REMOTE_STATUS_LABELS,
  REMOTE_STEER_ACTIONS,
  REMOTE_WORKER_STATE_LABELS,
  canActOnRemote,
  remoteActionBlocker,
  summarizeRemoteWorkers,
  workerProgressLabel,
  workerSteerBlocker,
  type RemoteFleet,
  type RemoteMachine,
  type RemoteSteerAction,
  type RemoteWorker,
  type RemoteWorkerState,
} from "./remote_fleet";

export const MOBILE_FLEET_SCHEMA = "simplicio.desktop-mobile-fleet/v1";
/** The widest layout this projection is allowed to call read-mostly. */
export const MOBILE_FLEET_MAX_WIDTH = 480;
/** Widths the responsive layout is specified and tested against. */
export const MOBILE_FLEET_TESTED_WIDTHS = [375, 480] as const;
export type FleetLayoutMode = "mobile" | "wide";

export const STEER_ACTION_LABELS: Record<RemoteSteerAction, string> = {
  pause: "Pausar",
  resume: "Retomar",
};

export type MobileFleetReasonCode =
  | "mobile_fleet_ready"
  | "mobile_fleet_empty"
  | "mobile_fleet_unavailable";

export interface MobileSteerView {
  action: RemoteSteerAction;
  label: string;
  enabled: boolean;
  /** Visible reason when disabled; null when the action may be sent. */
  blocker: string | null;
}

export interface MobileWorkerView {
  id: string;
  label: string;
  state: RemoteWorkerState;
  stateLabel: string;
  claim: string | null;
  claimLabel: string;
  progressLabel: string;
  receiptId: string | null;
  /** Empty when the controls must stay hidden (machine not authenticated/online). */
  steer: MobileSteerView[];
  /** Reason shown even when no control is rendered. */
  hiddenReason: string | null;
}

export interface MobileMachineView {
  id: string;
  label: string;
  url: string;
  status: RemoteMachine["status"];
  statusLabel: string;
  authenticated: boolean;
  versionLabel: string;
  latencyLabel: string;
  actionable: boolean;
  blocker: string | null;
  workers: MobileWorkerView[];
  receipts: string[];
  workersReason: string;
}

export interface MobileFleetSummary {
  machines: number;
  actionable: number;
  workers: number;
  running: number;
  paused: number;
  blocked: number;
  withReceipt: number;
}

export interface MobileFleetProjection {
  schema: typeof MOBILE_FLEET_SCHEMA;
  width: number;
  layout: FleetLayoutMode;
  maxWidthPx: number;
  reasonCode: MobileFleetReasonCode;
  summary: MobileFleetSummary;
  machines: MobileMachineView[];
}

/**
 * `<= 480 px` is the read-mostly mobile layout. Anything wider keeps the
 * existing panel: the breakpoint is one boundary, not two competing ones.
 */
export function fleetLayoutMode(width: number): FleetLayoutMode {
  if (!Number.isFinite(width) || width <= 0) return "wide";
  return width <= MOBILE_FLEET_MAX_WIDTH ? "mobile" : "wide";
}

function workerStateLabel(worker: RemoteWorker): string {
  return REMOTE_WORKER_STATE_LABELS[worker.state];
}

function projectWorker(remote: RemoteMachine, worker: RemoteWorker): MobileWorkerView {
  // A machine that is not online+authenticated hides every steering control;
  // the reason stays visible so the screen never looks broken.
  const hiddenReason = remoteActionBlocker(remote);
  const steer: MobileSteerView[] = hiddenReason !== null
    ? []
    : REMOTE_STEER_ACTIONS.map((action) => {
      const blocker = workerSteerBlocker(remote, worker, action);
      return {
        action,
        label: STEER_ACTION_LABELS[action],
        enabled: blocker === null,
        blocker,
      };
    });
  return {
    id: worker.id,
    label: worker.label,
    state: worker.state,
    stateLabel: workerStateLabel(worker),
    claim: worker.claim,
    claimLabel: worker.claim ?? "sem claim reportado",
    progressLabel: workerProgressLabel(worker),
    receiptId: worker.receiptId,
    steer,
    hiddenReason,
  };
}

function projectMachine(remote: RemoteMachine): MobileMachineView {
  const blocker = remoteActionBlocker(remote);
  const workers = (remote.workers ?? []).map((worker) => projectWorker(remote, worker));
  const receipts: string[] = [];
  for (const worker of remote.workers ?? []) {
    if (worker.receiptId !== null && !receipts.includes(worker.receiptId)) receipts.push(worker.receiptId);
  }
  return {
    id: remote.id,
    label: remote.label,
    url: remote.url,
    status: remote.status,
    statusLabel: REMOTE_STATUS_LABELS[remote.status],
    authenticated: remote.authenticated,
    versionLabel: remote.version === null ? "versão não informada" : `versão ${remote.version}`,
    latencyLabel: remote.latencyMs === null ? "latência não medida" : `${remote.latencyMs} ms`,
    actionable: canActOnRemote(remote),
    blocker,
    workers,
    receipts,
    workersReason: (remote.workers ?? []).length === 0
      ? "Nenhum worker reportado por esta máquina; nada é inventado."
      : "",
  };
}

/**
 * Build the mobile projection. `width` is passed in instead of read from the
 * DOM so the layout is a pure function the responsive tests can pin at 375 and
 * 480 px.
 */
export function buildMobileFleet(fleet: RemoteFleet | null, width: number): MobileFleetProjection {
  const layout = fleetLayoutMode(width);
  const remotes = fleet === null ? [] : fleet.remotes.slice(0, MAX_REMOTE_FLEET);
  const machines = remotes.map(projectMachine);
  const workerSummary = summarizeRemoteWorkers(remotes);
  const omitted = remotes.length === 0 || (fleet !== null && fleet.error !== null);
  const reasonCode: MobileFleetReasonCode = fleet === null
    ? "mobile_fleet_unavailable"
    : omitted
      ? "mobile_fleet_empty"
      : "mobile_fleet_ready";
  return {
    schema: MOBILE_FLEET_SCHEMA,
    width: Number.isFinite(width) ? Math.max(0, Math.round(width)) : 0,
    layout,
    maxWidthPx: MOBILE_FLEET_MAX_WIDTH,
    reasonCode,
    summary: {
      machines: remotes.length,
      actionable: remotes.filter(canActOnRemote).length,
      workers: workerSummary.total,
      running: workerSummary.running,
      paused: workerSummary.paused,
      blocked: workerSummary.blocked,
      withReceipt: workerSummary.withReceipt,
    },
    machines,
  };
}

/**
 * Where the Runtime-owned receipt is already reported. Used to prove that a
 * steer receipt is the same one the fleet (and therefore the activity
 * timeline) shows, instead of a client-minted id.
 */
export function receiptOwner(
  projection: MobileFleetProjection,
  receiptId: string,
): { machineId: string; workerId: string } | null {
  for (const machine of projection.machines) {
    const workers = (machine.workers as MobileWorkerView[] | undefined) ?? [];
    for (const worker of workers) {
      if (worker.receiptId === receiptId) {
        return { machineId: machine.id, workerId: worker.id };
      }
    }
  }
  return null;
}
