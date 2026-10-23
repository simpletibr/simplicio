import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { RemoteFleetList } from "./RemoteFleetPanel";
import {
  REMOTE_FLEET_SCHEMA,
  parseRemoteFleet,
  type RemoteFleet,
  type RemoteMachine,
} from "../remote_fleet";

const noop = () => undefined;

function machine(overrides: Partial<RemoteMachine>): RemoteMachine {
  return {
    id: "mac-mini",
    label: "Mac mini",
    url: "http://127.0.0.1:8787",
    status: "online",
    authenticated: true,
    version: "3.10.0",
    latencyMs: 18,
    reasonCode: null,
    ...overrides,
  };
}

function fleet(remotes: RemoteMachine[], configured = true): RemoteFleet {
  return parseRemoteFleet({
    schema: REMOTE_FLEET_SCHEMA,
    configured,
    redacted: true,
    observedAt: 1_900_000_000,
    error: null,
    remotes,
  });
}

function render(value: RemoteFleet | null, extra: { error?: string | null; selectedId?: string | null } = {}) {
  return renderToStaticMarkup(
    <RemoteFleetList
      fleet={value}
      busy={false}
      error={extra.error ?? null}
      selectedId={extra.selectedId ?? null}
      onRefresh={noop}
      onSelect={noop}
    />,
  );
}

describe("RemoteFleetList", () => {
  const value = fleet([
    machine({}),
    machine({
      id: "studio",
      label: "Studio",
      url: "https://studio.example.test",
      status: "offline",
      authenticated: false,
      version: null,
      latencyMs: null,
      reasonCode: "remote_unreachable",
    }),
    machine({
      id: "office",
      label: "Office",
      url: "https://office.example.test",
      status: "unauthorized",
      authenticated: false,
      version: null,
      latencyMs: 41,
      reasonCode: "remote_unauthorized",
    }),
  ]);

  it("shows every machine with status, version and latency", () => {
    const html = render(value);
    expect(html).toContain("Mac mini");
    expect(html).toContain("Studio");
    expect(html).toContain("Office");
    expect(html).toContain("Online");
    expect(html).toContain("Offline");
    expect(html).toContain("Não autorizado");
    expect(html).toContain("3.10.0");
    expect(html).toContain("18 ms");
    expect(html).toContain("1/3 online");
    expect(html).toContain("remote_unauthorized");
  });

  it("enables the per-machine action only for an online and authenticated remote", () => {
    const html = render(value);
    // Refresh stays available; the two unauthenticated rows are locked.
    expect((html.match(/disabled=""/g) ?? []).length).toBe(2);
    expect(html).toContain("A máquina está offline");
    expect(html).toContain("autorização");
    expect(html).toContain("Selecionar");
  });

  it("never renders a demo or a credential when the fleet is empty or unconfigured", () => {
    const empty = render(fleet([], false), { error: null });
    expect(empty).toContain("Nenhum runtime remoto configurado");
    expect(empty).toContain("desktop-remotes.json");
    expect(empty).not.toContain("Mac mini");
    expect(empty).not.toContain("Bearer");

    const preview = render(null, { error: "preview_no_runtime" });
    expect(preview).toContain("Prévia visual");
    expect(preview).not.toContain("demo");
    expect(preview).not.toContain("ghp_");
  });

  it("reports a local selection without claiming a remote action", () => {
    const html = render(value, { selectedId: "mac-mini" });
    expect(html).toContain("Máquina selecionada: Mac mini");
    expect(html).toContain("Nenhuma ação remota foi enviada");
  });
});
