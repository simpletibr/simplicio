import { useEffect, useMemo, useState } from "react";
import { createDesktopWorktree, loadDesktopWorktrees, removeDesktopWorktree } from "../bridge";
import {
  DEFAULT_WIP_LIMIT,
  createAllowed,
  fleetErrorMessage,
  fleetState,
  type Worktree,
} from "../fleet";

const AGENTS = ["claude", "codex", "gemini", "cursor", "opencode", "hermes"];

export function FleetCockpitList({
  worktrees,
  repoPath,
  issue,
  agent,
  wipLimit,
  busy,
  error,
  onRepo,
  onIssue,
  onAgent,
  onWipLimit,
  onCreate,
  onRemove,
}: {
  worktrees: Worktree[] | null;
  repoPath: string;
  issue: string;
  agent: string;
  wipLimit: number;
  busy: boolean;
  error?: string | null;
  onRepo: (value: string) => void;
  onIssue: (value: string) => void;
  onAgent: (value: string) => void;
  onWipLimit: (value: number) => void;
  onCreate: () => void;
  onRemove: (worktree: Worktree) => void;
}) {
  const state = useMemo(
    () => (worktrees ? fleetState(worktrees, wipLimit) : null),
    [worktrees, wipLimit],
  );
  return (
    <section className="panel fleet-cockpit" data-testid="fleet-cockpit" aria-label="Fleet cockpit">
      <div className="session-feed-heading">
        <div>
          <h2>Fleet cockpit</h2>
          <p>Um worktree por tarefa, com WIP limit por track e status derivado do git.</p>
        </div>
        <span className="neutral-badge">{state ? state.active + "/" + state.wipLimit + " WIP" : "sem dados"}</span>
      </div>
      <div className="fleet-controls">
        <label>Repositório<input value={repoPath} onChange={(event) => onRepo(event.target.value)} placeholder="C:/caminho/do/repo" /></label>
        <label>Issue<input type="number" min={1} value={issue} onChange={(event) => onIssue(event.target.value)} /></label>
        <label>Agente<select value={agent} onChange={(event) => onAgent(event.target.value)}>{AGENTS.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label>WIP limit<input type="number" min={1} max={64} value={wipLimit} onChange={(event) => onWipLimit(Number(event.target.value))} /></label>
        <button className="button button-primary" type="button" disabled={busy || (state ? !createAllowed(state) : false)} onClick={onCreate}>
          Criar worktree
        </button>
      </div>
      {state?.overLimit && <p role="status">WIP limit atingido; finalize uma tarefa antes de criar outra.</p>}
      {error && <p role="status">{fleetErrorMessage(error)}</p>}
      {state && (
        <ul className="fleet-list">
          {state.worktrees.map((worktree) => (
            <li key={worktree.path}>
              <strong>{worktree.main ? "main" : worktree.branch ?? "detached"}</strong>
              <span>{worktree.issue ? "issue #" + worktree.issue : "sem issue"}</span>
              <code>{worktree.path}</code>
              {!worktree.main && (
                <button className="button button-secondary" type="button" disabled={busy} onClick={() => onRemove(worktree)}>
                  Remover
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
      <p className="cache-meter-source">Criação git real em <code>~/.simplicio/worktrees/&lt;repo&gt;/issue-&lt;n&gt;</code>; remoção limitada a esse diretório. O WIP limit é aplicado antes de qualquer escrita.</p>
    </section>
  );
}

export function FleetCockpit() {
  const [repoPath, setRepoPath] = useState("");
  const [issue, setIssue] = useState("");
  const [agent, setAgent] = useState("claude");
  const [wipLimit, setWipLimit] = useState(DEFAULT_WIP_LIMIT);
  const [worktrees, setWorktrees] = useState<Worktree[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh(path = repoPath) {
    if (!path.trim()) return;
    try {
      setWorktrees(await loadDesktopWorktrees(path.trim()));
      setError(null);
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setError(code === "preview_no_runtime" ? null : code);
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function mutate(action: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await action();
      await refresh();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    } finally {
      setBusy(false);
    }
  }

  return (
    <FleetCockpitList
      worktrees={worktrees}
      repoPath={repoPath}
      issue={issue}
      agent={agent}
      wipLimit={wipLimit}
      busy={busy}
      error={error}
      onRepo={(value) => { setRepoPath(value); void refresh(value); }}
      onIssue={setIssue}
      onAgent={setAgent}
      onWipLimit={setWipLimit}
      onCreate={() => {
        const number = Number(issue);
        if (!Number.isSafeInteger(number) || number < 1) { setError("issue_invalid"); return; }
        void mutate(() => createDesktopWorktree(repoPath.trim(), number, agent, wipLimit));
      }}
      onRemove={(worktree) => void mutate(() => removeDesktopWorktree(repoPath.trim(), worktree.path))}
    />
  );
}
