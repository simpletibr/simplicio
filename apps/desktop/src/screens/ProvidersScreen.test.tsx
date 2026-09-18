import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { createDemoSnapshot } from "../demo";
import { ProvidersScreen } from "./ProvidersScreen";

describe("host plugin freshness", () => {
  it("renders Runtime plugin receipts without inventing catalog updates", () => {
    const html = renderToStaticMarkup(<ProvidersScreen
      snapshot={createDemoSnapshot("active")}
      busy={false}
      repairing={false}
      onRefresh={() => undefined}
      onRepair={async () => { throw new Error("unused"); }}
      onReconcile={async () => { throw new Error("unused"); }}
    />);
    expect(html).toContain("Skills e plugins instalados");
    expect(html).toContain('data-testid="host-plugin-freshness"');
    expect(html).toContain("Atual");
    expect(html).not.toContain("Run Grok");
    expect(html).not.toContain("atualizar agora");
    expect(html).not.toContain("0 plugins");
  });

  it("keeps unknown and unverified receipts distinct from current or zero", () => {
    const snapshot = createDemoSnapshot("active");
    snapshot.hostPlugins = {
      schema: "simplicio.desktop-host-plugins/v1",
      available: true,
      reconcileRequired: false,
      pendingCount: 0,
      pendingTruncated: false,
      state: "complete",
      revision: 1,
      receiptDigest: `sha256:${"2".repeat(64)}`,
      planDigest: `sha256:${"0".repeat(64)}`,
      hosts: [
        { host: "codex", status: "applied_unverified", reasonCode: "manager_readback_unknown", verification: "none" },
        { host: "claude", status: "unknown", reasonCode: "state_unknown", verification: "none" },
        { host: "hermes", status: "not_detected", reasonCode: "host_or_manager_not_detected", verification: "none" },
        { host: "opencode", status: "drifted", reasonCode: "manager_plugin_drifted", verification: "manager_version" },
      ],
    };
    const html = renderToStaticMarkup(<ProvidersScreen
      snapshot={snapshot}
      busy={false}
      repairing={false}
      onRefresh={() => undefined}
      onRepair={async () => { throw new Error("unused"); }}
      onReconcile={async () => { throw new Error("unused"); }}
    />);
    expect(html).toContain("Desconhecido");
    expect(html).toContain("Não detectado");
    expect(html).toContain("Desatualizado");
    expect(html).not.toContain("0 plugins");
    expect(html).not.toContain("atualizar agora");
  });

  it("does not show plugin receipts on the inventory-only agents page", () => {
    const html = renderToStaticMarkup(<ProvidersScreen
      snapshot={createDemoSnapshot("active")}
      busy={false}
      repairing={false}
      inventoryOnly
      onRefresh={() => undefined}
      onRepair={async () => { throw new Error("unused"); }}
      onReconcile={async () => { throw new Error("unused"); }}
    />);
    expect(html).not.toContain("Skills e plugins instalados");
  });
});
