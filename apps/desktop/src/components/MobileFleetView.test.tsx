import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MobileFleetView } from "./MobileFleetView";
import { MOBILE_FLEET_TESTED_WIDTHS } from "../mobile_fleet";
import {
  REMOTE_FLEET_SCHEMA,
  parseRemoteFleet,
  type RemoteFleet,
  type RemoteMachine,
  type RemoteWorker,
  type RemoteSteerReceipt,
} from "../remote_fleet";

const noop = () => undefined;

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

const receipt: RemoteSteerReceipt = {
  schema: "simplicio.desktop-fleet-steer/v1",
  machineId: "mac-mini",
  workerId: "w-1",
  action: "pause",
  receiptId: "rcpt-468-1",
  status: "sent",
};

function render(
  value: RemoteFleet | null,
  width: number,
  extra: {
    steerBusy?: string | null;
    steerReceipt?: RemoteSteerReceipt | null;
    steerError?: string | null;
    error?: string | null;
  } = {},
) {
  return renderToStaticMarkup(
    <MobileFleetView
      fleet={value}
      width={width}
      busy={false}
      error={extra.error ?? null}
      steerBusy={extra.steerBusy ?? null}
      steerReceipt={extra.steerReceipt ?? null}
      steerError={extra.steerError ?? null}
      onRefresh={noop}
      onSteer={noop}
    />,
  );
}

describe("MobileFleetView", () => {
  const online = machine();
  const offline = machine({
    id: "studio",
    label: "Studio",
    url: "https://studio.example.test",
    status: "offline",
    authenticated: false,
    version: null,
    latencyMs: null,
    reasonCode: "remote_unreachable",
  });
  const value = fleet([online, offline]);

  for (const width of MOBILE_FLEET_TESTED_WIDTHS) {
    it(`renders machines, workers, claims, progress and receipts at ${width}px`, () => {
      const html = render(value, width);
      expect(html).toContain(`data-layout="mobile"`);
      expect(html).toContain(`data-width="${width}"`);
      expect(html).toContain("Mac mini");
      expect(html).toContain("Studio");
      expect(html).toContain("issue-468");
      expect(html).toContain("Claim");
      expect(html).toContain("issue:468");
      expect(html).toContain("Progresso");
      expect(html).toContain("3/7 passo(s)");
      expect(html).toContain("rcpt-468-1");
      expect(html).toContain("2 máquina(s)");
      expect(html).toContain("1 acionável(is)");
      // Read-mostly only: no input can send free-form steering text.
      expect(html).not.toContain("<input");
      expect(html).not.toContain("<textarea");
    });
  }

  it("hides the steering controls when the machine is not online and authenticated", () => {
    const html = render(value, 375);
    // Only the actionable machine renders the two allowed controls.
    expect(html).toContain('data-testid="mobile-steer-mac-mini-w-1-pause"');
    expect(html).toContain('data-testid="mobile-steer-mac-mini-w-1-resume"');
    expect(html).not.toContain("mobile-steer-studio");
    // The reason stays visible instead of an unexplained empty row.
    expect(html).toContain("A máquina está offline");
  });

  it("renders the disabled action with a visible reason", () => {
    const html = render(value, 375);
    // Resume is offered but disabled while the worker runs, with its hint.
    expect(html).toMatch(/disabled="" aria-describedby="mobile-steer-hint-mac-mini-w-1-resume"/);
    expect(html).toContain("Só um worker pausado pode ser retomado.");
    // Pause is enabled for a running worker.
    expect(html).not.toMatch(/disabled=""[^>]*data-testid="mobile-steer-mac-mini-w-1-pause"/);
  });

  it("marks the in-flight action without unlocking the rest", () => {
    const html = render(value, 375, { steerBusy: "mac-mini/w-1/pause" });
    expect(html).toContain("Enviando…");
    expect(html).not.toMatch(/data-testid="mobile-steer-mac-mini-w-1-pause"[^>]*>Pausar/);
    expect(html).toMatch(/disabled=""[^>]*data-testid="mobile-steer-mac-mini-w-1-resume"/);
  });

  it("shows the runtime receipt as the same one the fleet reports", () => {
    const html = render(value, 375, { steerReceipt: receipt });
    expect(html).toContain('data-testid="mobile-fleet-steer-receipt"');
    expect(html).toContain("rcpt-468-1");
    expect(html).toContain("Mesmo recibo já reportado por w-1 em mac-mini");
    expect(html).toContain("timeline de Atividade");

    const unknown = render(value, 375, { steerReceipt: { ...receipt, receiptId: "rcpt-new-7" } });
    expect(unknown).toContain("rcpt-new-7");
    expect(unknown).toContain("A timeline de Atividade mostra este mesmo recibo");
  });

  it("states an unauthorized steer without pretending it succeeded", () => {
    const html = render(value, 375, { steerError: "fleet_steer_unauthorized" });
    expect(html).toContain('role="alert"');
    expect(html).toContain("dispositivo ou token não autorizado");
    expect(html).not.toContain("mobile-fleet-steer-receipt");
  });

  it("never renders a demo machine when the fleet is absent or empty", () => {
    const absent = render(null, 375);
    expect(absent).toContain("Frota remota ainda não consultada");
    expect(absent).not.toContain("Mac mini");

    const preview = render(null, 375, { error: "preview_no_runtime" });
    expect(preview).toContain("Prévia visual");
    expect(preview).not.toContain("Bearer");
    expect(preview).not.toContain("ghp_");

    const empty = render(fleet([]), 480);
    expect(empty).toContain("não declara nenhum runtime");
    expect(empty).not.toContain("mobile-steer-");
  });
});
