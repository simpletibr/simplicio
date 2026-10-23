import { useState } from "react";
import {
  commitDesktopReview,
  loadDesktopReview,
  pushDesktopReview,
  submitDesktopReview,
} from "../bridge";
import {
  autoMergeLabel,
  commitGuard,
  commitGuardLabel,
  commitMessageError,
  MAX_COMMIT_MESSAGE_CHARS,
  reviewErrorMessage,
  reviewView,
  type ReviewCommitReceipt,
  type ReviewDigest,
  type ReviewPushReceipt,
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
  commitMessage,
  commitConfirmed,
  createUpstream,
  commitReceipt,
  pushReceipt,
  commitError,
  pushError,
  onCommitMessage,
  onCommitConfirmed,
  onCreateUpstream,
  onCommit,
  onPush,
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
  commitMessage: string;
  commitConfirmed: boolean;
  createUpstream: boolean;
  commitReceipt: ReviewCommitReceipt | null;
  pushReceipt: ReviewPushReceipt | null;
  commitError?: string | null;
  pushError?: string | null;
  onCommitMessage: (value: string) => void;
  onCommitConfirmed: (value: boolean) => void;
  onCreateUpstream: (value: boolean) => void;
  onCommit: () => void;
  onPush: () => void;
}) {
  if (!review) {
    return (
      <section className="panel review-flow" data-testid="review-flow" aria-label="Revisão">
        <p role="status">{error ? reviewErrorMessage(error) : "Carregue um repositório para revisar o diff."}</p>
      </section>
    );
  }
  const view = reviewView(review, planDigest);
  const guard = commitGuard(view, review.truncated);
  const messageError = commitMessageError(commitMessage);
  const committed = commitReceipt?.status === "committed" ? commitReceipt : null;
  const pushed = pushReceipt?.status === "pushed" ? pushReceipt : null;
  const canCommit = !busy && guard === null && messageError === null && commitConfirmed;
  const canPush = !busy && !pushed && typeof committed?.sha === "string";
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
      <div className="review-git" data-testid="review-git" aria-label="Commit e push">
        <h3>Commit e push</h3>
        <p data-commit-guard={guard ?? "ready"}>{commitGuardLabel(guard)}</p>
        <label>
          Mensagem do commit
          <textarea
            value={commitMessage}
            maxLength={MAX_COMMIT_MESSAGE_CHARS}
            onChange={(event) => onCommitMessage(event.target.value)}
            placeholder="Mensagem que você digita; o commit usa só os arquivos revisados."
          />
        </label>
        <label className="review-confirm">
          <input
            type="checkbox"
            checked={commitConfirmed}
            disabled={busy || guard !== null}
            onChange={(event) => onCommitConfirmed(event.target.checked)}
          />
          Confirmo commitar {view.files.length} arquivo(s) revisado(s) com esta mensagem
        </label>
        {messageError && <p role="status">{reviewErrorMessage(messageError)}</p>}
        <div className="review-actions">
          <button
            className="button button-primary"
            type="button"
            disabled={!canCommit}
            onClick={onCommit}
            title={guard ? commitGuardLabel(guard) : "Cria um commit com o sha registrado no recibo."}
          >
            Commitar revisão
          </button>
          <label className="review-confirm">
            <input
              type="checkbox"
              checked={createUpstream}
              disabled={busy || !committed}
              onChange={(event) => onCreateUpstream(event.target.checked)}
            />
            Criar upstream <code>origin/&lt;branch&gt;</code> se a branch ainda não tiver
          </label>
          <button
            className="button button-secondary"
            type="button"
            disabled={!canPush}
            onClick={onPush}
            title="Só faz push de um commit registrado por esta revisão; nunca usa force."
          >
            Fazer push
          </button>
        </div>
        {commitError && <p role="alert">{reviewErrorMessage(commitError)}</p>}
        {commitReceipt?.status === "commit_failed" && (
          <p role="alert">
            O commit não foi criado{commitReceipt.code ? " (" + commitReceipt.code + ")" : ""}. O stderr real do git está abaixo.
          </p>
        )}
        {commitReceipt?.stderr && (
          <pre data-testid="review-commit-stderr" role="alert">{commitReceipt.stderr}</pre>
        )}
        {committed && (
          <div className="review-receipt" data-testid="review-commit-receipt" role="status">
            <p>Commit <code>{committed.sha}</code> em <code>{committed.branch}</code></p>
            <p>Recibo <code>{committed.path}</code> · {committed.paths.length} arquivo(s) · mensagem com {committed.message_chars} caractere(s)</p>
            <p>A mensagem não é gravada no recibo, apenas o digest; o sha acima é o commit real.</p>
            {pushed ? (
              <p>Push concluído em <code>{pushed.upstream}</code>{pushed.idempotent ? " (recibo reaproveitado, sem novo push)" : ""}.</p>
            ) : (
              <p>Ainda não há push registrado para este commit.</p>
            )}
            <p>Recarregue o diff para revisar o próximo estado da worktree.</p>
          </div>
        )}
        {pushError && <p role="alert">{reviewErrorMessage(pushError)}</p>}
        {pushReceipt?.status === "push_failed" && (
          <p role="alert">
            O push foi recusado{pushReceipt.code ? " (" + pushReceipt.code + ")" : ""}. O stderr real do git está abaixo.
          </p>
        )}
        {pushReceipt?.stderr && (
          <pre data-testid="review-push-stderr" role="alert">{pushReceipt.stderr}</pre>
        )}
      </div>
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
  const [commitMessage, setCommitMessage] = useState("");
  const [commitConfirmed, setCommitConfirmed] = useState(false);
  const [createUpstream, setCreateUpstream] = useState(false);
  const [commitReceipt, setCommitReceipt] = useState<ReviewCommitReceipt | null>(null);
  const [pushReceipt, setPushReceipt] = useState<ReviewPushReceipt | null>(null);
  const [commitError, setCommitError] = useState<string | null>(null);
  const [pushError, setPushError] = useState<string | null>(null);

  function resetGitState() {
    setCommitReceipt(null);
    setPushReceipt(null);
    setCommitError(null);
    setPushError(null);
    setCommitConfirmed(false);
    setCreateUpstream(false);
  }

  async function load() {
    if (!repoPath.trim()) return;
    setBusy(true);
    setError(null);
    setSubmitError(null);
    setReceipt(null);
    resetGitState();
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

  async function commit() {
    if (!review || !commitConfirmed) return;
    if (commitGuard(reviewView(review, planDigest), review.truncated) !== null) return;
    if (commitMessageError(commitMessage) !== null) return;
    setBusy(true);
    setCommitError(null);
    setPushReceipt(null);
    setPushError(null);
    try {
      setCommitReceipt(await commitDesktopReview(repoPath.trim(), review.digest, commitMessage, base));
      setCommitConfirmed(false);
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setCommitError(code === "preview_no_runtime" ? "review_unavailable" : code);
    } finally {
      setBusy(false);
    }
  }

  async function push() {
    const sha = commitReceipt?.sha;
    if (!commitReceipt || !sha) return;
    setBusy(true);
    setPushError(null);
    try {
      setPushReceipt(await pushDesktopReview(repoPath.trim(), commitReceipt.digest, sha, createUpstream));
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setPushError(code === "preview_no_runtime" ? "review_unavailable" : code);
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
        commitMessage={commitMessage}
        commitConfirmed={commitConfirmed}
        createUpstream={createUpstream}
        commitReceipt={commitReceipt}
        pushReceipt={pushReceipt}
        commitError={commitError}
        pushError={pushError}
        onCommitMessage={setCommitMessage}
        onCommitConfirmed={setCommitConfirmed}
        onCreateUpstream={setCreateUpstream}
        onCommit={() => void commit()}
        onPush={() => void push()}
      />
    </section>
  );
}
