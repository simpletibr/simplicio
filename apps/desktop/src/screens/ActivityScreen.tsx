import { useEffect, useMemo, useRef, useState } from "react";
import { exportDesktopSnapshot } from "../bridge";
import type { ActivityItem, DesktopSnapshot } from "../contracts";
import { Glyph } from "../components/Brand";
import { createActivityProjection } from "../activity_projection";
import {
  aiBomToJson,
  aiBomToMarkdown,
  buildAiBom,
  createReplay,
  mergeEventPages,
  type ActivityReplay,
  type DesktopEventPage,
  type ReplayRun,
} from "../activity_replay";
import type { DesktopUsageState } from "../usage_store";
import { searchMatches } from "../workbench";

type StatusFilter = "all" | ActivityItem["status"];

export function redactedActivity(items: ActivityItem[], savingsProven = false) {
  return items.map(({ id, title, provider, savedTokens, occurredAt, status }) => ({
    id, title, provider, savedTokens: savingsProven ? savedTokens : null, occurredAt, status,
  }));
}

function downloadActivity(items: ActivityItem[], savingsProven: boolean) {
  if (typeof document === "undefined") return;
  const payload = JSON.stringify({ schema: "simplicio.activity-export/v1", items: redactedActivity(items, savingsProven) }, null, 2);
  const url = URL.createObjectURL(new Blob([payload], { type: "application/json" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "simplicio-activity.json";
  link.click();
  URL.revokeObjectURL(url);
}

function downloadText(name: string, mime: string, text: string) {
  if (typeof document === "undefined") return;
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

function statusLabel(status: ActivityItem["status"]): string {
  return status === "verified" ? "verificado" : status === "running" ? "em execução" : "atenção";
}

function eventErrorLabel(error: unknown): string {
  const code = error instanceof Error ? error.message : String(error);
  switch (code) {
    case "preview_no_runtime":
      return "prévia sem daemon";
    case "activity_events_unavailable":
      return "daemon indisponível";
    case "activity_events_timeout":
      return "sem resposta do daemon";
    case "activity_events_cursor_invalid":
      return "cursor inválido";
    case "unsupported_schema":
    case "invalid_page":
    case "invalid_envelope":
    case "invalid_payload":
    case "invalid_cursor":
    case "page_too_large":
    case "page_too_many_events":
    case "activity_events_invalid":
    case "activity_events_invalid_event":
    case "activity_events_too_large":
    case "activity_events_too_many":
      return "página de eventos rejeitada";
    default:
      return "falha ao consultar o daemon";
  }
}

export function activityMatchesSearch(item: ActivityItem, query: string): boolean {
  return searchMatches([item.id, item.title, item.detail, item.provider, item.status].join(" "), query);
}

export interface ActivityScreenProps {
  snapshot: DesktopSnapshot;
  usage?: DesktopUsageState;
  /** Poll one bounded page from `desktop_activity_events`. Omit in preview. */
  loadEvents?: (afterCursor: number) => Promise<DesktopEventPage>;
  /** Last page already loaded; kept for static renders and tests. */
  initialEvents?: DesktopEventPage | null;
  /** Gap between long-polls; the 900 ms wait keeps latency under 1 s. */
  pollIntervalMs?: number;
}

function runOptionLabel(run: ReplayRun): string {
  const worktree = run.worktree === null ? "" : ` · ${run.worktree}`;
  return `${run.id}${worktree} · ${run.steps.length} passo(s)`;
}

export function ActivityScreen({
  snapshot,
  usage,
  loadEvents,
  initialEvents,
  pollIntervalMs = 250,
}: ActivityScreenProps) {
  const projection = createActivityProjection(snapshot);
  const savingsProven = snapshot.savings.proofKind === "measured" || snapshot.savings.proofKind === "replayed" || snapshot.savings.proofKind === "mixed";
  const [status, setStatus] = useState<StatusFilter>("all");
  const [provider, setProvider] = useState("all");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [exported, setExported] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [events, setEvents] = useState<DesktopEventPage | null>(initialEvents ?? null);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [stepLimit, setStepLimit] = useState<number | null>(null);
  const [bomSaved, setBomSaved] = useState<string | null>(null);
  const exportLock = useRef(false);
  const cursorRef = useRef(initialEvents?.nextCursor ?? 0);
  const pageSize = Math.max(1, Math.min(snapshot.limits.maxActivity, 5));
  const providers = useMemo(() => Array.from(new Set(projection.items.map((item) => item.provider))).sort(), [projection.items]);
  const filtered = projection.items.filter((item) => (status === "all" || item.status === status)
    && (provider === "all" || item.provider === provider)
    && activityMatchesSearch(item, query));
  const visible = filtered.slice(page * pageSize, (page + 1) * pageSize);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const safePage = Math.min(page, pageCount - 1);
  const shown = safePage === page ? visible : filtered.slice(safePage * pageSize, (safePage + 1) * pageSize);

  const replay: ActivityReplay | null = useMemo(
    () => (events === null ? null : createReplay(events)),
    [events],
  );
  const runs = replay?.runs ?? [];
  const activeRun = runs.find((run) => run.id === selectedRunId) ?? runs[0] ?? null;
  const activeSteps = activeRun === null ? [] : activeRun.steps;
  const shownSteps = stepLimit === null ? activeSteps : activeSteps.slice(0, stepLimit);

  useEffect(() => {
    if (!loadEvents || snapshot.source !== "runtime") return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const pull = async () => {
      setEventsLoading(true);
      try {
        const next = await loadEvents(cursorRef.current);
        if (cancelled) return;
        cursorRef.current = Math.max(cursorRef.current, next.nextCursor);
        setEvents((previous) => mergeEventPages(previous, next));
        setEventsError(null);
      } catch (error) {
        if (!cancelled) setEventsError(eventErrorLabel(error));
      } finally {
        if (!cancelled) {
          setEventsLoading(false);
          timer = setTimeout(() => void pull(), Math.max(200, pollIntervalMs));
        }
      }
    };
    void pull();
    return () => {
      cancelled = true;
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [loadEvents, pollIntervalMs, snapshot.source]);

  useEffect(() => {
    setStepLimit(null);
  }, [activeRun?.id]);

  function exportAiBom(format: "json" | "markdown") {
    if (replay === null) return;
    const bom = buildAiBom(replay, { source: snapshot.source === "runtime" ? "runtime" : "preview" });
    if (format === "json") {
      downloadText("simplicio-ai-bom.json", "application/json", aiBomToJson(bom));
      setBomSaved("simplicio-ai-bom.json");
    } else {
      downloadText("simplicio-ai-bom.md", "text/markdown", aiBomToMarkdown(bom));
      setBomSaved("simplicio-ai-bom.md");
    }
  }

  async function exportReceipts() {
    if (exportLock.current) return;
    exportLock.current = true; setExporting(true); setExported(null); setExportError(null);
    try {
      const path = await exportDesktopSnapshot("activity", { status, provider, search: query });
      if (path) setExported(path);
      else downloadActivity(filtered, savingsProven);
    } catch { setExportError("Não foi possível salvar os recibos em Downloads. Verifique as permissões e o espaço em disco."); }
    finally { exportLock.current = false; setExporting(false); }
  }

  return (
    <div className="page secondary-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Recibos</span>
          <h1>Atividade</h1>
          <p>Execuções, cache e economia com evidência limitada ao snapshot.</p>
          <p className="token-proof-note">Economia: <code>{snapshot.savings.proofKind}</code>{!savingsProven && " · indisponível neste recorte"}</p>
          <p className="token-proof-note">Changefeed da sessão: <code>{usage?.changefeed.connection ?? "offline"}</code> · {usage?.changefeed.projection ? "último snapshot do Runtime disponível" : "sem snapshot; economia não é inferida"}</p>
        </div>
        <button className="button button-secondary" type="button" disabled={exporting} onClick={() => void exportReceipts()}>{exporting ? "Exportando…" : "Exportar recibos"}</button>
      </section>
      {exported && <p className="export-feedback" role="status">Exportado para {exported}</p>}
      {exportError && <p className="inline-error" role="alert">{exportError}</p>}
      <section className="panel activity-page-panel">
        <div className="activity-toolbar">
          <label className="activity-search"><Glyph name="search" size={16} /><input type="search" aria-label="Buscar recibos" placeholder="Buscar recibos" value={query} maxLength={120} onChange={(event) => { setQuery(event.target.value); setPage(0); }} /></label>
          <div className="segmented-control" aria-label="Filtrar por estado">
            {(["all", "verified", "running", "attention"] as const).map((item) => (
              <button key={item} className={status === item ? "active" : ""} type="button" onClick={() => { setStatus(item); setPage(0); }}>
                {item === "all" ? "Todos" : statusLabel(item)}
              </button>
            ))}
          </div>
          <label className="activity-provider-filter">Provider
            <select value={provider} onChange={(event) => { setProvider(event.target.value); setPage(0); }}>
              <option value="all">Todos</option>
              {providers.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
        </div>
        <div className="activity-page-list">
          {shown.length === 0 ? <p className="empty-state">Nenhum recibo neste filtro.</p> : shown.map((item) => (
            <article className="activity-page-row" key={item.id}>
              <div className={`activity-status ${item.status === "attention" ? "attention" : ""}`}><Glyph name="activity" size={15} /></div>
              <div className="activity-copy"><strong>{item.title}</strong><p>{item.detail}</p><span>{item.provider} · {new Date(item.occurredAt).toLocaleString("pt-BR")}</span></div>
              <div className={`activity-saving${savingsProven ? "" : " muted"}`}><strong>{savingsProven ? `−${item.savedTokens.toLocaleString("pt-BR")}` : "—"}</strong><span>{savingsProven ? "tokens" : "sem evidência"}</span></div>
            </article>
          ))}
        </div>
        <footer className="activity-pagination">
          <span>{filtered.length} recibo(s) · máximo {projection.pageSize} · {projection.reasonCode}</span>
          <div><button className="text-button" type="button" disabled={safePage === 0} onClick={() => setPage((current) => Math.max(0, current - 1))}>Anterior</button><span>Página {safePage + 1} de {pageCount}</span><button className="text-button" type="button" disabled={safePage >= pageCount - 1} onClick={() => setPage((current) => Math.min(pageCount - 1, current + 1))}>Próxima</button></div>
        </footer>
      </section>

      <section className="panel activity-replay" data-testid="activity-replay">
        <div className="activity-replay-heading">
          <div>
            <span className="eyebrow">Flight recorder</span>
            <h2>Replay da execução</h2>
            <p className="token-proof-note">
              {events === null
                ? "Aguardando a primeira página do daemon de eventos."
                : `${events.events.length} evento(s) · cursor ${events.nextCursor} · ${events.hasMore ? "há mais no daemon" : "página completa"}${events.rejected > 0 ? ` · ${events.rejected} rejeitado(s)` : ""}`}
            </p>
            {eventsLoading && events === null && <p className="token-proof-note" role="status">Consultando o daemon…</p>}
            {eventsError && <p className="inline-error" role="alert">Eventos indisponíveis ({eventsError}). Nenhum evento é inventado.</p>}
          </div>
          <div className="activity-replay-actions">
            <button className="button button-secondary" type="button" disabled={replay === null || runs.length === 0} onClick={() => exportAiBom("json")}>AI-BOM (JSON)</button>
            <button className="button button-secondary" type="button" disabled={replay === null || runs.length === 0} onClick={() => exportAiBom("markdown")}>AI-BOM (Markdown)</button>
          </div>
        </div>
        {bomSaved && <p className="export-feedback" role="status">AI-BOM salvo como {bomSaved}</p>}
        {replay !== null && runs.length > 0 ? (
          <>
            <div className="activity-replay-toolbar">
              <label className="activity-provider-filter">Execução
                <select
                  aria-label="Selecionar execução"
                  value={activeRun?.id ?? ""}
                  onChange={(event) => { setSelectedRunId(event.target.value); setStepLimit(null); }}
                >
                  {runs.map((run) => <option key={run.id} value={run.id}>{runOptionLabel(run)}</option>)}
                </select>
              </label>
              <span className="activity-replay-meta">
                {activeRun === null ? "unknown" : `${activeRun.state} · ${activeRun.status}${activeRun.worktree ? ` · ${activeRun.worktree}` : ""}`}
              </span>
              <div className="activity-replay-playback">
                <button className="text-button" type="button" disabled={shownSteps.length === 0} onClick={() => setStepLimit((current) => Math.max(1, (current ?? activeSteps.length) - 1))}>Passo anterior</button>
                <span>{shownSteps.length} de {activeSteps.length} passo(s)</span>
                <button className="text-button" type="button" disabled={shownSteps.length >= activeSteps.length} onClick={() => setStepLimit((current) => Math.min(activeSteps.length, (current ?? activeSteps.length) + 1))}>Próximo passo</button>
              </div>
            </div>
            {activeRun !== null && activeRun.receipts.length > 0 && (
              <p className="token-proof-note">Recibos: {activeRun.receipts.map((receipt) => <code key={receipt}>{receipt}</code>)}</p>
            )}
            <ol className="activity-replay-steps">
              {shownSteps.length === 0 ? <li className="empty-state">Nenhum passo registrado para esta execução.</li> : shownSteps.map((step) => (
                <li key={`${step.cursor}-${step.sequence}`} className={`activity-replay-step ${step.status === "unknown" ? "status-unknown" : "status-recorded"}`}>
                  <span className="activity-replay-cursor">#{step.cursor}</span>
                  <div>
                    <strong>{step.label}</strong>
                    {step.detail && <p>{step.detail}</p>}
                    <span>{step.kind} · {step.status}{step.receiptId ? ` · recibo ${step.receiptId}` : ""}</span>
                  </div>
                </li>
              ))}
            </ol>
          </>
        ) : (
          <p className="empty-state">Sem eventos do daemon para reproduzir; o replay não fabrica passos.</p>
        )}
      </section>
    </div>
  );
}
