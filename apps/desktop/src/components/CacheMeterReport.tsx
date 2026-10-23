import {
  billedInputTokens,
  cacheBustCauses,
  formatCacheHitRate,
  formatPrefixReuse,
  type CacheMeterReceipt,
} from "../cache_meter";

export function CacheMeterReport({
  receipt,
  error,
}: {
  receipt?: CacheMeterReceipt | null;
  error?: string | null;
}) {
  if (!receipt) {
    if (!error) return null;
    return (
      <section
        className="panel token-evidence cache-meter-report"
        aria-label="Cache do prompt"
        data-testid="cache-meter-report"
      >
        <div className="session-feed-heading">
          <div>
            <h2>Cache do prompt</h2>
            <p>A medição do Runtime não está disponível; nenhum número foi estimado.</p>
          </div>
          <span className="neutral-badge">indisponível</span>
        </div>
        <p role="status"><code>{error}</code></p>
      </section>
    );
  }
  const billed = billedInputTokens(receipt);
  const hitRate = formatCacheHitRate(receipt.session_hit_rate, billed);
  if (receipt.status !== "measured" || hitRate === null) return null;
  const last = receipt.per_request.length > 0
    ? receipt.per_request[receipt.per_request.length - 1]
    : null;
  const prefixReuse = formatPrefixReuse(last?.prefix_reuse ?? null);
  return (
    <section
      className="panel token-evidence cache-meter-report"
      aria-label="Cache do prompt por sessão"
      data-testid="cache-meter-report"
    >
      <div className="session-feed-heading">
        <div>
          <h2>Cache do prompt</h2>
          <p>Taxa medida pelo Runtime para {receipt.requests} requisição(ões) da sessão.</p>
        </div>
        <span className="neutral-badge">medido</span>
      </div>
      <div className="report-task-facts">
        <div>
          <span>Taxa de acerto</span>
          <strong>{hitRate}</strong>
          <small>cache_read / (input + cache_read + cache_write)</small>
        </div>
        <div>
          <span>Reuso do prefixo</span>
          <strong>{prefixReuse ?? "—"}</strong>
          <small>última requisição</small>
        </div>
        <div>
          <span>Quebras de cache</span>
          <strong>{receipt.busts.length}</strong>
          <small>causas atribuídas pelo Runtime</small>
        </div>
      </div>
      {receipt.busts.length > 0 && (
        <ul className="cache-meter-busts" aria-label="Quebras de cache">
          {receipt.busts.map((bust) => (
            <li key={bust.request_index}>
              requisição #{bust.request_index}: esperado {bust.expected_read}, lido {bust.actual_read} ({cacheBustCauses(bust)})
            </li>
          ))}
        </ul>
      )}
      <p className="cache-meter-source">Valores vindos do recibo <code>simplicio.cache-meter/v1</code>; o Desktop não lê transcripts nem recalcula a taxa.</p>
    </section>
  );
}
