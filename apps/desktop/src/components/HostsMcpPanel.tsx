import { useEffect, useState } from "react";
import { hostStatusLabel, type HostWrite, type HostsPlan } from "../hosts_plan";
import { loadDesktopHostsPlan, repairDesktopHosts } from "../bridge";

export function HostsMcpList({
  plan,
  busy,
  error,
  onRepair,
}: {
  plan: HostsPlan | null;
  busy: boolean;
  error?: string | null;
  onRepair: () => void;
}) {
  if (!plan) {
    return (
      <section className="panel hosts-mcp-panel" data-testid="hosts-mcp-panel" aria-label="Hosts e MCP">
        <p role="status">{error ? "Plano de hosts indisponível: " + error : "Consultando hosts detectados…"}</p>
      </section>
    );
  }
  const divergent = plan.hosts.filter((host) => !host.compliant);
  return (
    <section className="panel hosts-mcp-panel" data-testid="hosts-mcp-panel" aria-label="Hosts e MCP">
      <div className="session-feed-heading">
        <div>
          <h2>Hosts e MCP</h2>
          <p>{plan.hosts.length} host(s) detectado(s); o binário gerenciado é {plan.binary ?? "não informado"}.</p>
        </div>
        <span className="neutral-badge">{divergent.length > 0 ? divergent.length + " divergente(s)" : plan.status}</span>
      </div>
      <table>
        <thead><tr><th>Host</th><th>Configuração</th><th>Perfil</th><th>Estado</th></tr></thead>
        <tbody>
          {plan.hosts.map((host: HostWrite) => (
            <tr key={host.label + host.path}>
              <td>{host.label}</td>
              <td><code>{host.path}</code></td>
              <td>{host.profile ?? (host.mapperOnlyRequired ? "não explícito" : "—")}</td>
              <td>{hostStatusLabel(host)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <button className="button button-primary" type="button" disabled={busy} onClick={onRepair}>
        Reparar registros
      </button>
      {error && <p role="status">{error}</p>}
      <p className="cache-meter-source">O reparo usa <code>simplicio mcp register</code>; perfis Claude/Hermes devem ser mapper-only. Versão/inode por processo não são inventados quando o Runtime não os expõe.</p>
    </section>
  );
}

export function HostsMcpPanel() {
  const [plan, setPlan] = useState<HostsPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setPlan(await loadDesktopHostsPlan());
      setError(null);
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setError(code === "preview_no_runtime" ? null : code);
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function repair() {
    setBusy(true);
    setError(null);
    try {
      await repairDesktopHosts();
      await refresh();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    } finally {
      setBusy(false);
    }
  }

  return <HostsMcpList plan={plan} busy={busy} error={error} onRepair={() => void repair()} />;
}
