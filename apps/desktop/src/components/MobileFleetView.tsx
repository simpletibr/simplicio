import {
  STEER_ACTION_LABELS,
  buildMobileFleet,
  receiptOwner,
  type MobileFleetProjection,
} from "../mobile_fleet";
import { remoteFleetErrorMessage, type RemoteFleet, type RemoteSteerAction, type RemoteSteerReceipt } from "../remote_fleet";

export interface MobileFleetViewProps {
  fleet: RemoteFleet | null;
  /** Viewport width in CSS pixels; the layout is a pure function of it. */
  width: number;
  busy: boolean;
  error?: string | null;
  /** `${machineId}/${workerId}/${action}` while a steer is in flight. */
  steerBusy?: string | null;
  steerReceipt?: RemoteSteerReceipt | null;
  steerError?: string | null;
  onRefresh: () => void;
  onSteer: (machineId: string, workerId: string, action: RemoteSteerAction) => void;
}

function steerKey(machineId: string, workerId: string, action: RemoteSteerAction): string {
  return `${machineId}/${workerId}/${action}`;
}

function ReceiptNote({ receipt, projection }: { receipt: RemoteSteerReceipt; projection: MobileFleetProjection }) {
  const owner = receiptOwner(projection, receipt.receiptId);
  return (
    <p className="mobile-fleet-receipt" role="status" data-testid="mobile-fleet-steer-receipt">
      <span>Recibo do Runtime</span>
      <code>{receipt.receiptId}</code>
      <small>
        {owner === null
          ? "Ação confirmada pelo Runtime. A timeline de Atividade mostra este mesmo recibo assim que o evento chega."
          : `Mesmo recibo já reportado por ${owner.workerId} em ${owner.machineId}; a timeline de Atividade mostra este mesmo id.`}
      </small>
    </p>
  );
}

/**
 * Read-mostly narrow layout (<= 480 px). It reuses the single fleet projection
 * the panel already loaded — no extra fetch — and only exposes pause/resume of
 * a worker when the machine is online and accepted our token.
 */
export function MobileFleetView({
  fleet,
  width,
  busy,
  error = null,
  steerBusy = null,
  steerReceipt = null,
  steerError = null,
  onRefresh,
  onSteer,
}: MobileFleetViewProps) {
  const projection = buildMobileFleet(fleet, width);

  return (
    <section
      className="panel mobile-fleet"
      data-testid="mobile-fleet"
      data-layout={projection.layout}
      data-width={projection.width}
      data-reason={projection.reasonCode}
      aria-label="Frota remota"
    >
      <header className="mobile-fleet-heading">
        <span className="eyebrow">HOSTS REMOTOS</span>
        <h2>Frota remota</h2>
        <p>
          {projection.summary.machines} máquina(s) · {projection.summary.workers} worker(s) ·{" "}
          {projection.summary.actionable} acionável(is)
        </p>
        <button
          className="button button-secondary"
          type="button"
          onClick={onRefresh}
          disabled={busy}
          aria-label="Atualizar frota remota"
        >
          {busy ? "Consultando…" : "Atualizar"}
        </button>
      </header>

      {error && <p role="status" className="mobile-fleet-message">{remoteFleetErrorMessage(error)}</p>}
      {fleet?.error && <p role="status" className="mobile-fleet-message">{remoteFleetErrorMessage(fleet.error)}</p>}
      {steerError && (
        <p role="alert" className="mobile-fleet-message" data-testid="mobile-fleet-steer-error">
          {remoteFleetErrorMessage(steerError)}
        </p>
      )}

      {steerReceipt && <ReceiptNote receipt={steerReceipt} projection={projection} />}

      {projection.machines.length === 0 && (
        <p className="mobile-fleet-empty">
          {fleet === null
            ? "Frota remota ainda não consultada neste dispositivo. Nenhuma máquina é inventada."
            : fleet.configured
              ? "O arquivo de máquinas remotas não declara nenhum runtime."
              : "Nenhum runtime remoto configurado. Crie ~/.simplicio/desktop-remotes.json com o schema simplicio.desktop-remotes/v1."}
        </p>
      )}

      <ul className="mobile-fleet-machines">
        {projection.machines.map((machine) => {
          return (
            <li key={machine.id} className="mobile-fleet-machine" data-status={machine.status} data-testid={`mobile-machine-${machine.id}`}>
              <div className="mobile-fleet-machine-head">
                <strong>{machine.label}</strong>
                <span className={"mobile-fleet-status mobile-fleet-status-" + machine.status}>{machine.statusLabel}</span>
              </div>
              <code className="mobile-fleet-url">{machine.url}</code>
              <dl className="mobile-fleet-meta">
                <div><dt>Versão</dt><dd>{machine.versionLabel}</dd></div>
                <div><dt>Latência</dt><dd>{machine.latencyLabel}</dd></div>
                <div><dt>Token</dt><dd>{machine.authenticated ? "aceito" : "não confirmado"}</dd></div>
              </dl>

              {machine.workersReason !== "" && <p className="mobile-fleet-note">{machine.workersReason}</p>}

              {machine.workers.length > 0 && (
                <ul className="mobile-fleet-workers">
                  {machine.workers.map((worker) => (
                    <li key={worker.id} className="mobile-fleet-worker" data-state={worker.state} data-testid={`mobile-worker-${machine.id}-${worker.id}`}>
                      <div className="mobile-fleet-worker-head">
                        <strong>{worker.label}</strong>
                        <span className="mobile-fleet-worker-state">{worker.stateLabel}</span>
                      </div>
                      <p className="mobile-fleet-claim"><span>Claim</span> <code>{worker.claimLabel}</code></p>
                      <p className="mobile-fleet-progress"><span>Progresso</span> {worker.progressLabel}</p>
                      {worker.receiptId !== null && (
                        <p className="mobile-fleet-worker-receipt"><span>Recibo</span> <code>{worker.receiptId}</code></p>
                      )}

                      {worker.hiddenReason !== null && (
                        <p className="mobile-fleet-blocker">{worker.hiddenReason}</p>
                      )}

                      {worker.steer.length > 0 && (
                        <div className="mobile-fleet-actions">
                          {worker.steer.map((view) => {
                            const key = steerKey(machine.id, worker.id, view.action);
                            const hintId = `mobile-steer-hint-${key.replace(/[^A-Za-z0-9_-]/g, "-")}`;
                            return (
                              <div key={view.action} className="mobile-fleet-action">
                                <button
                                  className="button button-secondary"
                                  type="button"
                                  disabled={!view.enabled || steerBusy !== null}
                                  aria-describedby={view.blocker === null ? undefined : hintId}
                                  onClick={() => onSteer(machine.id, worker.id, view.action)}
                                  data-testid={`mobile-steer-${machine.id}-${worker.id}-${view.action}`}
                                >
                                  {steerBusy === key ? "Enviando…" : STEER_ACTION_LABELS[view.action]}
                                </button>
                                {view.blocker !== null && <small id={hintId}>{view.blocker}</small>}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              {machine.receipts.length > 0 && (
                <p className="mobile-fleet-receipts">
                  <span>Recibos</span> {machine.receipts.map((receipt) => <code key={receipt}>{receipt}</code>)}
                </p>
              )}
            </li>
          );
        })}
      </ul>

      <footer className="mobile-fleet-footnote">
        <p>
          Layout estreito somente leitura sobre <code>/v1/health</code>. A única ação remota é pausar ou retomar um
          worker, e ela só aparece com a máquina online e o token aceito. Nenhum recibo é gerado por este app: o id
          vem do Runtime e é o mesmo exibido na timeline de Atividade.
        </p>
        <p>Largura {projection.width} px · breakpoint {projection.maxWidthPx} px · limite de scroll horizontal: 0.</p>
      </footer>
    </section>
  );
}
