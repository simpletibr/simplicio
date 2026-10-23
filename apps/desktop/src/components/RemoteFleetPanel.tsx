import { useCallback, useEffect, useRef, useState } from "react";
import { loadDesktopRemoteFleet, steerRemoteWorker } from "../bridge";
import { fleetLayoutMode } from "../mobile_fleet";
import { useViewportWidth } from "../use_viewport_width";
import {
  REMOTE_STATUS_LABELS,
  canActOnRemote,
  canSteerWorker,
  remoteActionBlocker,
  remoteFleetErrorMessage,
  summarizeRemoteFleet,
  type RemoteFleet,
  type RemoteMachine,
  type RemoteSteerAction,
  type RemoteSteerReceipt,
} from "../remote_fleet";
import { MobileFleetView } from "./MobileFleetView";
import "../mobile_fleet.css";

/**
 * Read-mostly fleet view. Rendering never invokes a remote action: the only
 * per-machine control selects a row locally, and it is disabled unless the
 * native projection proved the remote is online and accepted our token.
 */
export function RemoteFleetList({
  fleet,
  busy,
  error,
  selectedId,
  onRefresh,
  onSelect,
}: {
  fleet: RemoteFleet | null;
  busy: boolean;
  error?: string | null;
  selectedId?: string | null;
  onRefresh: () => void;
  onSelect: (remote: RemoteMachine) => void;
}) {
  const summary = fleet ? summarizeRemoteFleet(fleet.remotes) : null;
  const selected = fleet?.remotes.find((remote) => remote.id === selectedId && canActOnRemote(remote)) ?? null;
  return (
    <section className="panel remote-fleet" data-testid="remote-fleet" aria-label="Frota remota">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">HOSTS REMOTOS</span>
          <h2>Frota remota</h2>
          <p>Runtimes Simplicio em outras máquinas, com estado consultado por HTTP e sem expor credenciais.</p>
        </div>
        <div className="remote-fleet-heading-actions">
          <span className="neutral-badge">
            {summary ? summary.online + "/" + summary.total + " online" : "sem consulta"}
          </span>
          <button
            className="button button-secondary"
            type="button"
            onClick={onRefresh}
            disabled={busy}
            aria-label="Atualizar frota remota"
          >
            {busy ? "Consultando…" : "Atualizar frota"}
          </button>
        </div>
      </div>

      {error && <p role="status" className="remote-fleet-message">{remoteFleetErrorMessage(error)}</p>}
      {fleet?.error && <p role="status" className="remote-fleet-message">{remoteFleetErrorMessage(fleet.error)}</p>}

      {fleet && fleet.remotes.length === 0 && !fleet.error && (
        <p className="remote-fleet-empty">
          {fleet.configured
            ? "O arquivo de máquinas remotas não declara nenhum runtime. Nenhuma máquina foi inventada nesta consulta."
            : "Nenhum runtime remoto configurado. Crie ~/.simplicio/desktop-remotes.json com o schema simplicio.desktop-remotes/v1; tokens ficam em variáveis de ambiente, nunca no arquivo."}
        </p>
      )}

      {fleet && fleet.remotes.length > 0 && (
        <ul className="remote-fleet-list">
          {fleet.remotes.map((remote) => {
            const blocker = remoteActionBlocker(remote);
            const hintId = "remote-fleet-hint-" + remote.id;
            return (
              <li key={remote.id} data-status={remote.status} className="remote-fleet-item">
                <div className="remote-fleet-item-heading">
                  <div className="remote-fleet-identity">
                    <strong>{remote.label}</strong>
                    <code>{remote.id} · {remote.url}</code>
                  </div>
                  <span className={"remote-fleet-status remote-fleet-status-" + remote.status}>
                    {REMOTE_STATUS_LABELS[remote.status]}
                  </span>
                </div>
                <div className="remote-fleet-meta">
                  <span>versão {remote.version ?? "não informada"}</span>
                  <span>{remote.latencyMs === null ? "latência não medida" : remote.latencyMs + " ms"}</span>
                  <span>{remote.authenticated ? "token aceito" : "sem token confirmado"}</span>
                  <span>{(remote.workers ?? []).length} worker(s)</span>
                  {remote.reasonCode && <span>motivo: {remote.reasonCode}</span>}
                </div>
                <div className="remote-fleet-actions">
                  <small id={hintId}>{blocker ?? "Seleção local; nenhum comando é enviado ao runtime remoto."}</small>
                  <button
                    className="button button-secondary"
                    type="button"
                    disabled={blocker !== null}
                    aria-describedby={hintId}
                    onClick={() => onSelect(remote)}
                  >
                    Selecionar
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {selected && (
        <p role="status" className="remote-fleet-selection">
          Máquina selecionada: {selected.label} ({REMOTE_STATUS_LABELS[selected.status]}). Nenhuma ação remota foi enviada.
        </p>
      )}

      <p className="remote-fleet-footnote">
        Consulta somente leitura a <code>/v1/health</code>, com 3s por máquina, sem redirecionamentos e sem corpo
        ilimitado. Ações de controle remoto exigem autorização própria e ainda não são enviadas por esta versão.
      </p>
    </section>
  );
}

export function RemoteFleetPanel() {
  const [fleet, setFleet] = useState<RemoteFleet | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [steerBusy, setSteerBusy] = useState<string | null>(null);
  const [steerReceipt, setSteerReceipt] = useState<RemoteSteerReceipt | null>(null);
  const [steerError, setSteerError] = useState<string | null>(null);
  const width = useViewportWidth();
  const alive = useRef(false);
  const lock = useRef(false);
  const steerLock = useRef(false);

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  const refresh = useCallback(async () => {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    try {
      const next = await loadDesktopRemoteFleet();
      if (alive.current) {
        setFleet(next);
        setError(null);
      }
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      if (alive.current) {
        setFleet(null);
        setError(code);
      }
    } finally {
      lock.current = false;
      if (alive.current) setBusy(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const steer = useCallback(
    async (machineId: string, workerId: string, action: RemoteSteerAction) => {
      if (steerLock.current) return;
      const machine = fleet?.remotes.find((remote) => remote.id === machineId) ?? null;
      const worker = machine?.workers?.find((item) => item.id === workerId) ?? null;
      // The same gate the buttons use: an action that the projection does not
      // authorize is never sent, even if it is invoked programmatically.
      if (machine === null || worker === null || !canSteerWorker(machine, worker, action)) {
        setSteerError(
          machine === null || worker === null ? "fleet_steer_machine_unknown" : "fleet_steer_action_invalid",
        );
        return;
      }
      steerLock.current = true;
      setSteerBusy(`${machineId}/${workerId}/${action}`);
      setSteerError(null);
      try {
        const receipt = await steerRemoteWorker(machineId, workerId, action);
        if (alive.current) {
          setSteerReceipt(receipt);
          // The receipt must come back from the fleet, not from this client.
          void refresh();
        }
      } catch (failure) {
        const code = failure instanceof Error ? failure.message : String(failure);
        if (alive.current) setSteerError(code);
      } finally {
        steerLock.current = false;
        if (alive.current) setSteerBusy(null);
      }
    },
    [fleet, refresh],
  );

  if (fleetLayoutMode(width) === "mobile") {
    return (
      <MobileFleetView
        fleet={fleet}
        width={width}
        busy={busy}
        error={error}
        steerBusy={steerBusy}
        steerReceipt={steerReceipt}
        steerError={steerError}
        onRefresh={() => void refresh()}
        onSteer={(machineId, workerId, action) => void steer(machineId, workerId, action)}
      />
    );
  }

  return (
    <RemoteFleetList
      fleet={fleet}
      busy={busy}
      error={error}
      selectedId={selectedId}
      onRefresh={() => void refresh()}
      onSelect={(remote) => setSelectedId(remote.id)}
    />
  );
}
