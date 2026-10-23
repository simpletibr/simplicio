import { useState } from "react";
import { loadDesktopReview, submitDesktopReview } from "../bridge";
import {
  autoMergeLabel,
  reviewErrorMessage,
  reviewView,
  type ReviewDigest,
  type ReviewSubmissionReceipt,
} from "../review";

export function ReviewFlowCard({
  review,
  comments,
  planDigest,
  receipt,
  busy,
  error,
  submitError,
  onComments,
  onCopy,
  onSubmit,
}: {
  review: ReviewDigest | null;
  comments: string;
  planDigest: string;
  receipt: ReviewSubmissionReceipt | null;
  busy: boolean;
  error?: string | null;
  submitError?: string | null;
  onComments: (value: string) => void;
  onCopy: () => void;
  onSubmit: () => void;
}) {
  if (!review) {
    return (
      <section className="panel review-flow" data-testid="review-flow" aria-label="Revisão">
        <p role="status">{error ? reviewErrorMessage(error) : "Carregue um repositório para revisar o diff."}</p>
      </section>
    );
  }
  const view = reviewView(review, planDigest);
  return (
    <section className="panel review-flow" data-testid="review-flow" aria-label="Revisão">
      <div className="session-feed-heading">
        <div>
          <h2>Revisão</h2>
          <p>{view.files.length} arquivo(s) · +{view.additions} / -{view.deletions} · digest <code>{review.digest.slice(0, 19)}…</code></p>
        </div>
        <span
          className="neutral-badge"
          data-auto-merge={view.autoMerge.reason}
          title={"Motivo do auto-merge: " + view.autoMerge.reason}
        >
          {autoMergeLabel(view.autoMerge)}
        </span>
      </div>
      {review.truncated && <p role="status">Diff truncado em 200 KB; a revisão não está completa e o auto-merge fica bloqueado.</p>}
      {!planDigest.trim() && (
        <p>Sem plan digest no campo: o envio tenta ler <code>.simplicio/plan-digest</code> e o recibo mostra o motivo definitivo do auto-merge.</p>
      )}
      {view.flags.length > 0 && (
        <ul className="review-flags" aria-label="Flags de guardrail">
          {view.flags.map((flag) => <li key={flag.path}>{flag.kind}: <code>{flag.path}</code></li>)}
        </ul>
      )}
      <div className="review-files">
        {view.files.map((file) => (
          <details key={file.path} open>
            <summary>{file.path} <span>+{file.additions} / -{file.deletions}</span></summary>
            {file.hunks.map((hunk, index) => (
              <pre key={index} aria-label={"hunk " + file.path}>
                {hunk.header + "\n" + hunk.lines.join("\n")}
              </pre>
            ))}
          </details>
        ))}
      </div>
      <label>Comentários para o agente<textarea value={comments} maxLength={20_000} onChange={(event) => onComments(event.target.value)} placeholder="Comentários inline em Markdown. Envie para o inbox do agente ou copie para a sessão." /></label>
      <div className="review-actions">
        <button className="button button-secondary" type="button" disabled={busy || !comments.trim()} onClick={onCopy}>Copiar comentários</button>
        <button className="button button-primary" type="button" disabled={busy || !comments.trim()} onClick={onSubmit}>Enviar ao agente</button>
      </div>
      {submitError && <p role="alert">{reviewErrorMessage(submitError)}</p>}
      {receipt && (
        <div className="review-receipt" data-testid="review-receipt" role="status">
          <h3>Recibo do inbox</h3>
          <p>Receipt <code>{receipt.receipt_id}</code> · arquivo <code>{receipt.path}</code></p>
          <p>{receipt.idempotent ? "Entrega repetida: o receipt existente foi reaproveitado." : "Nova entrega gravada no inbox."}</p>
          <p>{autoMergeLabel(receipt.auto_merge)}</p>
          <p>O agente não é notificado em tempo real. A entrega verificada é este arquivo do inbox; a skill do agente o lê antes do próximo turno.</p>
        </div>
      )}
      {error && <p role="status">{reviewErrorMessage(error)}</p>}
    </section>
  );
}

export function ReviewFlow() {
  const [repoPath, setRepoPath] = useState("");
  const [base, setBase] = useState("");
  const [planDigest, setPlanDigest] = useState("");
  const [review, setReview] = useState<ReviewDigest | null>(null);
  const [comments, setComments] = useState("");
  const [receipt, setReceipt] = useState<ReviewSubmissionReceipt | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function load() {
    if (!repoPath.trim()) return;
    setBusy(true);
    setError(null);
    setSubmitError(null);
    setReceipt(null);
    try {
      setReview(await loadDesktopReview(repoPath.trim(), base));
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setError(code === "preview_no_runtime" ? null : code);
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(comments);
    } catch {
      setError("clipboard_unavailable");
    }
  }

  async function submit() {
    if (!review) return;
    setBusy(true);
    setSubmitError(null);
    try {
      setReceipt(await submitDesktopReview(repoPath.trim(), review.digest, comments, planDigest, base));
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setSubmitError(code === "preview_no_runtime" ? "review_unavailable" : code);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel review-flow-shell" aria-label="Revisão de código">
      <div className="fleet-controls">
        <label>Repositório<input value={repoPath} onChange={(event) => setRepoPath(event.target.value)} placeholder="C:/caminho/do/repo" /></label>
        <label>Base (opcional)<input value={base} onChange={(event) => setBase(event.target.value)} placeholder="main" /></label>
        <label>Plan digest (opcional)<input value={planDigest} onChange={(event) => setPlanDigest(event.target.value)} placeholder="sha256:… (vazio lê .simplicio/plan-digest)" /></label>
        <button className="button button-primary" type="button" disabled={busy} onClick={() => void load()}>Carregar diff</button>
      </div>
      <ReviewFlowCard
        review={review}
        comments={comments}
        planDigest={planDigest}
        receipt={receipt}
        busy={busy}
        error={error}
        submitError={submitError}
        onComments={setComments}
        onCopy={() => void copy()}
        onSubmit={() => void submit()}
      />
    </section>
  );
}
