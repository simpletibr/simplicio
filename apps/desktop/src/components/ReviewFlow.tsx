import { useState } from "react";
import { loadDesktopReview } from "../bridge";
import { reviewErrorMessage, reviewView, type ReviewDigest } from "../review";

export function ReviewFlowCard({
  review,
  comments,
  busy,
  error,
  onComments,
  onCopy,
}: {
  review: ReviewDigest | null;
  comments: string;
  busy: boolean;
  error?: string | null;
  onComments: (value: string) => void;
  onCopy: () => void;
}) {
  if (!review) {
    return (
      <section className="panel review-flow" data-testid="review-flow" aria-label="Revisão">
        <p role="status">{error ? reviewErrorMessage(error) : "Carregue um repositório para revisar o diff."}</p>
      </section>
    );
  }
  const view = reviewView(review);
  return (
    <section className="panel review-flow" data-testid="review-flow" aria-label="Revisão">
      <div className="session-feed-heading">
        <div>
          <h2>Revisão</h2>
          <p>{view.files.length} arquivo(s) · +{view.additions} / -{view.deletions} · digest <code>{review.digest.slice(0, 19)}…</code></p>
        </div>
        <span className="neutral-badge">{view.autoMerge.eligible ? "auto-merge elegível" : "auto-merge: " + view.autoMerge.reason}</span>
      </div>
      {review.truncated && <p role="status">Diff truncado em 200 KB; a revisão não está completa.</p>}
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
      <label>Comentários para o agente<textarea value={comments} maxLength={20_000} onChange={(event) => onComments(event.target.value)} placeholder="Comentários inline em Markdown; copie para a sessão do agente." /></label>
      <button className="button button-secondary" type="button" disabled={busy || !comments.trim()} onClick={onCopy}>Copiar comentários</button>
      {error && <p role="status">{reviewErrorMessage(error)}</p>}
    </section>
  );
}

export function ReviewFlow() {
  const [repoPath, setRepoPath] = useState("");
  const [base, setBase] = useState("");
  const [review, setReview] = useState<ReviewDigest | null>(null);
  const [comments, setComments] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!repoPath.trim()) return;
    setBusy(true);
    setError(null);
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

  return (
    <section className="panel review-flow-shell" aria-label="Revisão de código">
      <div className="fleet-controls">
        <label>Repositório<input value={repoPath} onChange={(event) => setRepoPath(event.target.value)} placeholder="C:/caminho/do/repo" /></label>
        <label>Base (opcional)<input value={base} onChange={(event) => setBase(event.target.value)} placeholder="main" /></label>
        <button className="button button-primary" type="button" disabled={busy} onClick={() => void load()}>Carregar diff</button>
      </div>
      <ReviewFlowCard review={review} comments={comments} busy={busy} error={error} onComments={setComments} onCopy={() => void copy()} />
    </section>
  );
}
