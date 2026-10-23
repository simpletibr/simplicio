import { useEffect, useMemo, useState } from "react";
import {
  createDesktopWorktree,
  loadDesktopFleetQueue,
  loadDesktopWorktrees,
  orientDesktopWorktree,
  removeDesktopWorktree,
  upsertDesktopFleetTask,
} from "../bridge";
import {
  DEFAULT_WIP_LIMIT,
  createAllowed,
  fleetErrorMessage,
  fleetState,
  type Worktree,
} from "../fleet";
import {
  DEFAULT_TRACK_WIP,
  FLEET_STATUSES,
  FLEET_STATUS_LABELS,
  admitFleetTask,
  emptyFleetQueue,
  fleetQueueErrorMessage,
  isFleetStatus,
  projectFleetQueue,
  type FleetQueue,
  type FleetStatus,
  type FleetTask,
  type FleetTaskNode,
} from "../fleet_queue";
import {
  orientationFields,
  orientationNotice as orientationMessage,
  type OrientationMeasurement,
} from "../worktree_orientation";

const AGENTS = ["claude", "codex", "gemini", "cursor", "opencode", "hermes"];
const TRACK_SUGGESTIONS = ["desktop", "runtime", "docs", "infra"];

export interface FleetQueueDraft {
  issue: number;
  agent: string;
  track: string;
  wave: number;
  status: FleetStatus;
  parent: string | null;
  trackWip: number;
}

function codeOf(failure: unknown): string {
  return failure instanceof Error ? failure.message : String(failure);
}

export function FleetTaskCard({
  task,
  busy,
  onStatus,
}: {
  task: FleetTask;
  busy: boolean;
  onStatus?: (id: string, status: FleetStatus) => void;
}) {
  const measured = typeof task.orientation_ms === "number";
  return (
    <article className="fleet-task" data-task={task.id}>
      <div className="fleet-task-head">
        <strong>{task.id}</strong>
        <span>#{task.issue}</span>
      </div>
      <p className="fleet-task-meta">{task.track} · wave {task.wave} · {task.agent}</p>
      {task.parent && <p className="fleet-task-parent">filho de {task.parent}</p>}
      <div className="fleet-task-footer">
        <span className={"fleet-orientation" + (measured ? "" : " unmeasured")}>
          {measured ? task.orientation_ms + " ms" : "orientação não medida"}
        </span>
        {onStatus ? (
          <select
            aria-label={"Status de " + task.id}
            value={task.status}
            disabled={busy}
            onChange={(event) => {
              if (isFleetStatus(event.target.value)) onStatus(task.id, event.target.value);
            }}
          >
            {FLEET_STATUSES.map((status) => (
              <option key={status} value={status}>{FLEET_STATUS_LABELS[status]}</option>
            ))}
          </select>
        ) : (
          <span className="neutral-badge">{FLEET_STATUS_LABELS[task.status]}</span>
        )}
      </div>
    </article>
  );
}

export function FleetTreeNode({ node, depth }: { node: FleetTaskNode; depth: number }) {
  return (
    <li data-depth={depth}>
      <span>{node.task.id}</span>
      {node.task.parent && <small> · filho de {node.task.parent}</small>}
      {node.children.length > 0 && (
        <ul>
          {node.children.map((child) => (
            <FleetTreeNode key={child.task.id} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}

export function FleetQueueBoard({
  queue,
  busy,
  onStatus,
}: {
  queue: FleetQueue;
  busy: boolean;
  onStatus?: (id: string, status: FleetStatus) => void;
}) {
  const board = useMemo(() => projectFleetQueue(queue), [queue]);
  return (
    <div className="fleet-queue" data-testid="fleet-queue" aria-label="Fleet queue board">
      <div className="fleet-queue-heading">
        <div>
          <h3>Fila da fleet</h3>
          <p>Lanes fixas por status; o WIP por track é verificado antes de qualquer escrita.</p>
        </div>
        <span className="neutral-badge">{board.counts.active} ativas · {board.counts.total} tarefas</span>
      </div>
      {board.tracks.length > 0 && (
        <div className="fleet-track-badges">
          {board.tracks.map((track) => (
            <span
              key={track.name}
              className={"fleet-track-badge" + (track.atLimit ? " at-limit" : "")}
              data-track={track.name}
              data-over={track.overLimit ? "true" : "false"}
            >
              {track.name} · {track.activeWip}/{track.limit} WIP{track.overLimit ? " · acima do limite" : ""}
            </span>
          ))}
        </div>
      )}
      <div className="fleet-lanes">
        {board.lanes.map((lane) => (
          <section key={lane.name} className="fleet-lane" data-lane={lane.name}>
            <h4>{lane.label} <span>{lane.tasks.length}</span></h4>
            {lane.tasks.length === 0 ? (
              <p className="fleet-lane-empty">—</p>
            ) : (
              lane.tasks.map((task) => (
                <FleetTaskCard key={task.id} task={task} busy={busy} onStatus={onStatus} />
              ))
            )}
          </section>
        ))}
      </div>
      {board.waves.length > 0 && (
        <div className="fleet-waves" data-testid="fleet-waves">
          {board.waves.map((wave) => (
            <p key={wave.wave}>
              <strong>Wave {wave.wave}</strong> · {wave.tasks.length} tarefa(s) · {wave.tracks.join(", ")}
            </p>
          ))}
        </div>
      )}
      <div className="fleet-tree" data-testid="fleet-tree">
        <h4>Pai/filho</h4>
        {board.roots.length === 0 ? (
          <p className="fleet-lane-empty">Sem tarefas na fila.</p>
        ) : (
          <ul>{board.roots.map((node) => <FleetTreeNode key={node.task.id} node={node} depth={0} />)}</ul>
        )}
      </div>
    </div>
  );
}

export function FleetQueueControls({
  busy,
  defaultIssue,
  defaultAgent,
  onAdd,
}: {
  busy: boolean;
  defaultIssue: string;
  defaultAgent: string;
  onAdd: (draft: FleetQueueDraft) => void;
}) {
  const [issue, setIssue] = useState(defaultIssue);
  const [track, setTrack] = useState(TRACK_SUGGESTIONS[0]);
  const [wave, setWave] = useState("1");
  const [status, setStatus] = useState<FleetStatus>("queued");
  const [parent, setParent] = useState("");
  const [trackWip, setTrackWip] = useState(String(DEFAULT_TRACK_WIP));
  const [localError, setLocalError] = useState<string | null>(null);

  function add() {
    const number = Number(issue);
    if (!Number.isSafeInteger(number) || number < 1) { setLocalError("issue_invalid"); return; }
    const waveNumber = Number(wave);
    if (!Number.isSafeInteger(waveNumber) || waveNumber < 1 || waveNumber > 9999) { setLocalError("wave_invalid"); return; }
    const limit = Number(trackWip);
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 64) { setLocalError("wip_limit_invalid"); return; }
    if (!track.trim()) { setLocalError("track_invalid"); return; }
    setLocalError(null);
    onAdd({
      issue: number,
      agent: defaultAgent,
      track: track.trim(),
      wave: waveNumber,
      status,
      parent: parent.trim() || null,
      trackWip: limit,
    });
  }

  return (
    <div className="fleet-queue-controls" data-testid="fleet-queue-controls">
      <label>Issue<input type="number" min={1} value={issue} onChange={(event) => setIssue(event.target.value)} /></label>
      <label>Track<input list="fleet-tracks" value={track} onChange={(event) => setTrack(event.target.value)} /></label>
      <datalist id="fleet-tracks">{TRACK_SUGGESTIONS.map((item) => <option key={item} value={item} />)}</datalist>
      <label>Wave<input type="number" min={1} max={9999} value={wave} onChange={(event) => setWave(event.target.value)} /></label>
      <label>Status<select value={status} onChange={(event) => { if (isFleetStatus(event.target.value)) setStatus(event.target.value); }}>
        {FLEET_STATUSES.map((item) => <option key={item} value={item}>{FLEET_STATUS_LABELS[item]}</option>)}
      </select></label>
      <label>Pai<input value={parent} onChange={(event) => setParent(event.target.value)} placeholder="id opcional" /></label>
      <label>WIP/track<input type="number" min={1} max={64} value={trackWip} onChange={(event) => setTrackWip(event.target.value)} /></label>
      <button className="button button-secondary" type="button" disabled={busy} onClick={add}>Adicionar à fila</button>
      {localError && <p role="status">{fleetQueueErrorMessage(localError)}</p>}
    </div>
  );
}

export function FleetCockpitList({
  worktrees,
  repoPath,
  issue,
  agent,
  wipLimit,
  busy,
  error,
  queue,
  queueError,
  orientationNotice,
  onCreate,
  onRemove,
  onRepo,
  onIssue,
  onAgent,
  onWipLimit,
  onQueueTask,
  onQueueStatus,
}: {
  worktrees: Worktree[] | null;
  repoPath: string;
  issue: string;
  agent: string;
  wipLimit: number;
  busy: boolean;
  error?: string | null;
  queue?: FleetQueue | null;
  queueError?: string | null;
  orientationNotice?: string | null;
  onRepo: (value: string) => void;
  onIssue: (value: string) => void;
  onAgent: (value: string) => void;
  onWipLimit: (value: number) => void;
  onCreate: () => void;
  onRemove: (worktree: Worktree) => void;
  onQueueTask?: (draft: FleetQueueDraft) => void;
  onQueueStatus?: (id: string, status: FleetStatus) => void;
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
      {onQueueTask && <FleetQueueControls busy={busy} defaultIssue={issue} defaultAgent={agent} onAdd={onQueueTask} />}
      {orientationNotice && (
        <p role="status" data-testid="fleet-orientation-notice">{orientationNotice}</p>
      )}
      {queue && <FleetQueueBoard queue={queue} busy={busy} onStatus={onQueueStatus} />}
      {queueError && <p role="status" data-testid="fleet-queue-error">{fleetQueueErrorMessage(queueError)}</p>}
      <p className="cache-meter-source">Criação git real em <code>~/.simplicio/worktrees/&lt;repo&gt;/issue-&lt;n&gt;</code>; remoção limitada a esse diretório. O WIP limit é aplicado antes de qualquer escrita. A orientação é medida no Runtime a partir do baseline compartilhado do default branch; sem baseline o tempo não é inventado e o motivo aparece acima.</p>
    </section>
  );
}

export function FleetCockpit() {
  const [repoPath, setRepoPath] = useState("");
  const [issue, setIssue] = useState("");
  const [agent, setAgent] = useState("claude");
  const [wipLimit, setWipLimit] = useState(DEFAULT_WIP_LIMIT);
  const [worktrees, setWorktrees] = useState<Worktree[] | null>(null);
  const [queue, setQueue] = useState<FleetQueue | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [orientation, setOrientation] = useState<{ issue: number; measurement: OrientationMeasurement } | null>(null);
  const [orientationNotice, setOrientationNotice] = useState<string | null>(null);

  async function refresh(path = repoPath) {
    if (!path.trim()) return;
    try {
      setWorktrees(await loadDesktopWorktrees(path.trim()));
      setError(null);
    } catch (failure) {
      const code = codeOf(failure);
      setError(code === "preview_no_runtime" ? null : code);
    }
  }

  async function refreshQueue(path = repoPath) {
    try {
      setQueue(await loadDesktopFleetQueue(path.trim()));
      setQueueError(null);
    } catch (failure) {
      const code = codeOf(failure);
      setQueueError(code === "preview_no_runtime" ? null : code);
    }
  }

  useEffect(() => { void refresh(); void refreshQueue(); }, []);

  async function mutate(action: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await action();
      await refresh();
    } catch (failure) {
      setError(codeOf(failure));
    } finally {
      setBusy(false);
    }
  }

  async function saveQueue(task: FleetTask, limits?: Record<string, number>) {
    setBusy(true);
    setQueueError(null);
    try {
      setQueue(await upsertDesktopFleetTask(repoPath.trim(), task, limits));
    } catch (failure) {
      setQueueError(codeOf(failure));
    } finally {
      setBusy(false);
    }
  }

  function addQueueTask(draft: FleetQueueDraft) {
    void (async () => {
      const current = queue ?? emptyFleetQueue();
      const matched = worktrees?.find((item) => item.issue === draft.issue);
      // Opening a task measures its orientation once, from the shared
      // baseline; a task without a real measurement is stored unmeasured.
      let measured = orientation && orientation.issue === draft.issue ? orientation.measurement : undefined;
      if (measured === undefined && matched) {
        try {
          const opened = await orientDesktopWorktree(repoPath.trim(), matched.path);
          setOrientation(opened.status === "measured" ? { issue: draft.issue, measurement: opened } : null);
          setOrientationNotice(orientationMessage(opened));
          measured = opened;
        } catch (failure) {
          setOrientationNotice("Falha ao medir a orientação: " + codeOf(failure));
        }
      }
      const task: FleetTask = {
        id: draft.issue + "-" + draft.track,
        issue: draft.issue,
        worktree: matched?.path ?? "",
        agent: draft.agent,
        track: draft.track,
        lane: draft.status,
        wave: draft.wave,
        status: draft.status,
        parent: draft.parent,
        updated_at: new Date().toISOString(),
        ...orientationFields(measured),
      };
      const limits = { ...current.wip_per_track, [draft.track]: draft.trackWip };
      const admission = admitFleetTask(current, task, limits);
      if (!admission.ok) { setQueueError(admission.error); return; }
      void saveQueue(task, { [draft.track]: draft.trackWip });
    })();
  }

  function updateQueueStatus(id: string, status: FleetStatus) {
    if (!queue) return;
    const existing = queue.tasks.find((item) => item.id === id);
    if (!existing) return;
    const task: FleetTask = { ...existing, status, lane: status, updated_at: new Date().toISOString() };
    const admission = admitFleetTask(queue, task);
    if (!admission.ok) { setQueueError(admission.error); return; }
    void saveQueue(task);
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
      queue={queue}
      queueError={queueError}
      orientationNotice={orientationNotice}
      onRepo={(value) => { setRepoPath(value); void refresh(value); void refreshQueue(value); }}
      onIssue={setIssue}
      onAgent={setAgent}
      onWipLimit={setWipLimit}
      onCreate={() => {
        const number = Number(issue);
        if (!Number.isSafeInteger(number) || number < 1) { setError("issue_invalid"); return; }
        void mutate(async () => {
          const receipt = await createDesktopWorktree(repoPath.trim(), number, agent, wipLimit);
          setOrientation(
            receipt.orientation.status === "measured"
              ? { issue: receipt.issue, measurement: receipt.orientation }
              : null,
          );
          setOrientationNotice(orientationMessage(receipt.orientation));
        });
      }}
      onRemove={(worktree) => void mutate(() => removeDesktopWorktree(repoPath.trim(), worktree.path))}
      onQueueTask={addQueueTask}
      onQueueStatus={updateQueueStatus}
    />
  );
}
