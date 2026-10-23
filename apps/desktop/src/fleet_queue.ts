export const FLEET_QUEUE_SCHEMA = "simplicio.fleet-queue/v1";
export const FLEET_QUEUE_PROJECTION_SCHEMA = "simplicio.fleet-queue-projection/v1";
export const FLEET_STATUSES = ["queued", "running", "blocked", "needs_review", "done"] as const;
export type FleetStatus = (typeof FLEET_STATUSES)[number];

export const FLEET_STATUS_LABELS: Record<FleetStatus, string> = {
  queued: "Na fila",
  running: "Executando",
  blocked: "Bloqueada",
  needs_review: "Revisão",
  done: "Concluída",
};

export const DEFAULT_TRACK_WIP = 5;
export const MAX_FLEET_TASKS = 512;
const MAX_ORIENTATION_MS = 86_400_000;
const SLUG = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const TRACK = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$/;

export interface FleetTask {
  id: string;
  issue: number;
  worktree: string;
  agent: string;
  track: string;
  lane: FleetStatus;
  wave: number;
  status: FleetStatus;
  parent: string | null;
  updated_at: string;
  /** Only present when a real start was measured; never synthesized. */
  started_at?: string;
  /** Only present when a real orientation measurement exists; never synthesized. */
  orientation_ms?: number;
}

export type FleetTaskDraft = Omit<FleetTask, "lane" | "updated_at"> & {
  lane?: FleetStatus;
  updated_at?: string;
};

export interface FleetQueue {
  schema: typeof FLEET_QUEUE_SCHEMA;
  wip_per_track: Record<string, number>;
  tasks: FleetTask[];
}

export interface FleetTaskNode {
  task: FleetTask;
  children: FleetTaskNode[];
}

export interface FleetLaneProjection {
  name: FleetStatus;
  label: string;
  tasks: FleetTask[];
}

export interface FleetTrackProjection {
  name: string;
  limit: number;
  activeWip: number;
  atLimit: boolean;
  overLimit: boolean;
  tasks: FleetTask[];
}

export interface FleetWaveProjection {
  wave: number;
  tracks: string[];
  tasks: FleetTask[];
}

export interface FleetQueueProjection {
  schema: typeof FLEET_QUEUE_PROJECTION_SCHEMA;
  lanes: FleetLaneProjection[];
  tracks: FleetTrackProjection[];
  waves: FleetWaveProjection[];
  roots: FleetTaskNode[];
  counts: Record<FleetStatus, number> & { total: number; active: number; done: number };
  orientation: { measured: number; unmeasured: number; median_ms: number | null };
}

export type FleetAdmission =
  | { ok: true; task: FleetTask; queue: FleetQueue; track: string; active: number; limit: number }
  | { ok: false; error: string; track?: string; active?: number; limit?: number };

function record(value: unknown, code: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(code);
  return value as Record<string, unknown>;
}

export function isFleetStatus(value: unknown): value is FleetStatus {
  return typeof value === "string" && (FLEET_STATUSES as readonly string[]).includes(value);
}

function validSlug(value: string): boolean {
  return SLUG.test(value);
}

function validTrack(value: string): boolean {
  return TRACK.test(value);
}

function validTimestamp(value: string): boolean {
  return TIMESTAMP.test(value);
}

function positiveInteger(value: unknown, code: string, max: number): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 1 || value > max) {
    throw new Error(code);
  }
  return value;
}

function nullableString(value: unknown, code: string): string | null {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value !== "string") throw new Error(code);
  return value;
}

function normalizeLimits(value: unknown): Record<string, number> {
  if (value === undefined || value === null) return {};
  const source = record(value, "wip_limit_invalid");
  const limits: Record<string, number> = {};
  for (const [track, limit] of Object.entries(source)) {
    if (!validTrack(track)) throw new Error("wip_limit_invalid");
    limits[track] = positiveInteger(limit, "wip_limit_invalid", 64);
  }
  return limits;
}

/** Validate and canonicalize one task. Optional measurement fields are preserved only when real. */
export function normalizeFleetTask(value: unknown, options: { stamp?: boolean } = {}): FleetTask {
  const source = record(value, "task_invalid");
  const id = source.id;
  if (typeof id !== "string" || !validSlug(id)) throw new Error("task_id_invalid");
  const issue = positiveInteger(source.issue, "issue_invalid", 10_000_000);
  const worktree = source.worktree;
  if (typeof worktree !== "string" || worktree.length > 4096 || /[\u0000-\u001f]/.test(worktree)) {
    throw new Error("worktree_invalid");
  }
  const agent = source.agent;
  if (typeof agent !== "string" || agent.length === 0 || agent.length > 64 || !/^[A-Za-z0-9._ -]+$/.test(agent)) {
    throw new Error("agent_invalid");
  }
  const track = source.track;
  if (typeof track !== "string" || !validTrack(track)) throw new Error("track_invalid");
  const wave = positiveInteger(source.wave, "wave_invalid", 9999);
  if (!isFleetStatus(source.status)) throw new Error("status_invalid");
  const status = source.status;
  const laneValue = source.lane === undefined || source.lane === null || source.lane === "" ? status : source.lane;
  if (!isFleetStatus(laneValue)) throw new Error("status_invalid");
  if (laneValue !== status) throw new Error("lane_status_mismatch");
  const parent = nullableString(source.parent, "parent_invalid");
  if (parent !== null && !validSlug(parent)) throw new Error("parent_invalid");

  let updatedAt: string;
  if (typeof source.updated_at === "string" && source.updated_at.length > 0) {
    if (!validTimestamp(source.updated_at)) throw new Error("updated_at_invalid");
    updatedAt = source.updated_at;
  } else if (source.updated_at === undefined && options.stamp !== false) {
    updatedAt = new Date().toISOString();
  } else {
    throw new Error("updated_at_invalid");
  }

  const task: FleetTask = {
    id,
    issue,
    worktree,
    agent,
    track,
    lane: status,
    wave,
    status,
    parent,
    updated_at: updatedAt,
  };

  if (source.started_at !== undefined && source.started_at !== null) {
    if (typeof source.started_at !== "string" || !validTimestamp(source.started_at)) throw new Error("started_at_invalid");
    task.started_at = source.started_at;
  }
  if (source.orientation_ms !== undefined && source.orientation_ms !== null) {
    const measured = source.orientation_ms;
    if (typeof measured !== "number" || !Number.isSafeInteger(measured) || measured < 0 || measured > MAX_ORIENTATION_MS) {
      throw new Error("orientation_invalid");
    }
    task.orientation_ms = measured;
  }
  return task;
}

export function sortFleetTasks(tasks: FleetTask[]): FleetTask[] {
  return [...tasks].sort((left, right) => {
    if (left.wave !== right.wave) return left.wave - right.wave;
    if (left.track !== right.track) return left.track.localeCompare(right.track);
    return left.id.localeCompare(right.id);
  });
}

function assertHierarchy(tasks: FleetTask[]): void {
  const byId = new Map<string, FleetTask>();
  for (const task of tasks) {
    if (byId.has(task.id)) throw new Error("task_duplicate");
    byId.set(task.id, task);
  }
  for (const task of tasks) {
    if (task.parent === task.id) throw new Error("task_cycle");
    if (task.parent !== null && !byId.has(task.parent)) throw new Error("parent_unknown:" + task.parent);
  }
  for (const task of tasks) {
    const seen = new Set<string>([task.id]);
    let cursor = task.parent;
    while (cursor !== null) {
      if (seen.has(cursor)) throw new Error("task_cycle");
      seen.add(cursor);
      cursor = byId.get(cursor)?.parent ?? null;
    }
  }
}

export function emptyFleetQueue(wipPerTrack: Record<string, number> = {}): FleetQueue {
  return { schema: FLEET_QUEUE_SCHEMA, wip_per_track: normalizeLimits(wipPerTrack), tasks: [] };
}

export function parseFleetQueue(value: unknown): FleetQueue {
  const source = record(value, "fleet_queue_invalid");
  if (source.schema !== FLEET_QUEUE_SCHEMA) throw new Error("fleet_queue_invalid");
  if (!Array.isArray(source.tasks)) throw new Error("fleet_queue_invalid");
  if (source.tasks.length > MAX_FLEET_TASKS) throw new Error("task_limit_reached");
  const tasks = source.tasks.map((task) => normalizeFleetTask(task, { stamp: false }));
  assertHierarchy(tasks);
  return {
    schema: FLEET_QUEUE_SCHEMA,
    wip_per_track: normalizeLimits(source.wip_per_track),
    tasks: sortFleetTasks(tasks),
  };
}

/** Idempotent merge by id. Re-upserting the same task with the same updated_at yields the same queue. */
export function upsertFleetTask(queue: FleetQueue, task: FleetTaskDraft | FleetTask): FleetQueue {
  const candidate = normalizeFleetTask(task);
  const known = queue.tasks.some((item) => item.id === candidate.id);
  if (!known && queue.tasks.length >= MAX_FLEET_TASKS) throw new Error("task_limit_reached");
  const tasks = queue.tasks.filter((item) => item.id !== candidate.id).concat(candidate);
  assertHierarchy(tasks);
  return { schema: FLEET_QUEUE_SCHEMA, wip_per_track: { ...queue.wip_per_track }, tasks: sortFleetTasks(tasks) };
}

/** Count non-done tasks in a track; queued work already consumes the track slot. */
export function trackActiveWip(queue: FleetQueue, track: string, exceptId?: string): number {
  return queue.tasks.filter((task) => task.track === track && task.id !== exceptId && task.status !== "done").length;
}

export function trackLimit(queue: FleetQueue, limits: Record<string, number>, track: string): number {
  return limits[track] ?? queue.wip_per_track[track] ?? DEFAULT_TRACK_WIP;
}

/** Authoritative pre-check mirrored by the Rust command; rejects before any write. */
export function admitFleetTask(
  queue: FleetQueue,
  draft: FleetTaskDraft | FleetTask,
  limits: Record<string, number> = queue.wip_per_track,
): FleetAdmission {
  let candidate: FleetTask;
  try {
    candidate = normalizeFleetTask(draft);
  } catch (failure) {
    return { ok: false, error: failure instanceof Error ? failure.message : String(failure) };
  }
  let normalizedLimits: Record<string, number>;
  try {
    normalizedLimits = normalizeLimits({ ...queue.wip_per_track, ...limits });
  } catch (failure) {
    return { ok: false, error: failure instanceof Error ? failure.message : String(failure) };
  }
  let next: FleetQueue;
  try {
    next = upsertFleetTask(queue, candidate);
  } catch (failure) {
    return { ok: false, error: failure instanceof Error ? failure.message : String(failure), track: candidate.track };
  }
  const limit = trackLimit(queue, normalizedLimits, candidate.track);
  const active = trackActiveWip(queue, candidate.track, candidate.id);
  if (candidate.status !== "done" && active >= limit) {
    return {
      ok: false,
      error: "wip_limit_reached:" + candidate.track,
      track: candidate.track,
      active,
      limit,
    };
  }
  return { ok: true, task: candidate, queue: next, track: candidate.track, active, limit };
}

function nodeFor(task: FleetTask, byId: Map<string, FleetTask>, seen: Set<string>): FleetTaskNode {
  const children = seen.has(task.id)
    ? []
    : [...byId.values()].filter((item) => item.parent === task.id).map((item) => nodeFor(item, byId, new Set([...seen, task.id])));
  children.sort((left, right) => left.task.id.localeCompare(right.task.id));
  return { task, children };
}

/** Deterministic board projection: stable lane, track, wave and parent/child ordering. */
export function projectFleetQueue(queue: FleetQueue): FleetQueueProjection {
  const tasks = sortFleetTasks(queue.tasks);
  const lanes = FLEET_STATUSES.map((status) => ({
    name: status,
    label: FLEET_STATUS_LABELS[status],
    tasks: tasks.filter((task) => task.status === status),
  }));

  const trackNames = [...new Set(tasks.map((task) => task.track))].sort((left, right) => left.localeCompare(right));
  const tracks = trackNames.map((name) => {
    const trackTasks = tasks.filter((task) => task.track === name);
    const limit = queue.wip_per_track[name] ?? DEFAULT_TRACK_WIP;
    const activeWip = trackTasks.filter((task) => task.status !== "done").length;
    return {
      name,
      limit,
      activeWip,
      atLimit: activeWip >= limit,
      overLimit: activeWip > limit,
      tasks: trackTasks,
    };
  });

  const waveNumbers = [...new Set(tasks.map((task) => task.wave))].sort((left, right) => left - right);
  const waves = waveNumbers.map((wave) => {
    const waveTasks = tasks.filter((task) => task.wave === wave);
    return {
      wave,
      tracks: [...new Set(waveTasks.map((task) => task.track))].sort((left, right) => left.localeCompare(right)),
      tasks: waveTasks,
    };
  });

  const byId = new Map(tasks.map((task) => [task.id, task]));
  const roots = tasks
    .filter((task) => task.parent === null || !byId.has(task.parent))
    .map((task) => nodeFor(task, byId, new Set()))
    .sort((left, right) => left.task.id.localeCompare(right.task.id));

  const counts = { queued: 0, running: 0, blocked: 0, needs_review: 0, done: 0, total: tasks.length, active: 0 };
  for (const task of tasks) {
    counts[task.status] += 1;
    if (task.status !== "done") counts.active += 1;
  }

  const measured = tasks.filter((task) => typeof task.orientation_ms === "number");
  const measurements = measured.map((task) => task.orientation_ms as number).sort((left, right) => left - right);
  const median = measurements.length === 0
    ? null
    : measurements.length % 2 === 1
      ? measurements[(measurements.length - 1) / 2]
      : Math.round((measurements[measurements.length / 2 - 1] + measurements[measurements.length / 2]) / 2);

  return {
    schema: FLEET_QUEUE_PROJECTION_SCHEMA,
    lanes,
    tracks,
    waves,
    roots,
    counts,
    orientation: {
      measured: measured.length,
      unmeasured: tasks.length - measured.length,
      median_ms: median,
    },
  };
}

export function fleetQueueErrorMessage(code: string): string {
  const [base, detail] = code.split(":");
  if (base === "wip_limit_reached") {
    return detail
      ? "Limite de WIP da track \"" + detail + "\" atingido. Mova uma tarefa para done, aumente o limite da track ou escolha outra track antes de admitir a tarefa."
      : "Limite de WIP da track atingido. Mova uma tarefa para done antes de admitir outra.";
  }
  if (base === "parent_unknown") return "A tarefa pai \"" + (detail ?? "") + "\" não existe na fila; escolha uma tarefa existente ou deixe o pai em branco.";
  if (base === "task_cycle") return "A hierarquia pai/filho formaria um ciclo; escolha outro pai para a tarefa.";
  if (base === "task_duplicate") return "Já existe uma tarefa com esse id na fila; atualize a existente em vez de duplicar.";
  if (base === "task_limit_reached") return "A fila atingiu o limite de tarefas; conclua ou remova tarefas antes de adicionar outra.";
  if (base === "issue_invalid") return "Informe uma issue válida (inteiro positivo).";
  if (base === "track_invalid") return "Informe uma track válida (letras, números, ponto, hífen ou sublinhado).";
  if (base === "wave_invalid") return "Informe uma wave válida (inteiro entre 1 e 9999).";
  if (base === "status_invalid") return "Status inválido; use queued, running, blocked, needs_review ou done.";
  if (base === "lane_status_mismatch") return "A lane precisa ser igual ao status da tarefa.";
  if (base === "agent_invalid") return "Agente inválido; use letras, números, espaço, ponto, hífen ou sublinhado.";
  if (base === "worktree_invalid") return "Caminho de worktree inválido.";
  if (base === "wip_limit_invalid") return "Limite de WIP inválido; use um inteiro entre 1 e 64.";
  if (base === "parent_invalid") return "Id da tarefa pai inválido.";
  if (base === "task_invalid") return "Tarefa inválida; confira id, issue, track, wave e status.";
  if (base === "orientation_invalid" || base === "started_at_invalid") return "Medição de orientação inválida; o campo só aceita valores realmente medidos.";
  if (base === "fleet_queue_invalid") return "Arquivo da fila da fleet inválido; verifique o estado persistido antes de continuar.";
  if (base === "fleet_queue_unavailable") return "Não foi possível ler ou gravar a fila da fleet; verifique o acesso ao diretório de estado.";
  if (base === "preview_no_runtime") return "Abra o app desktop para operar a fila; a prévia não altera o repositório.";
  return "Falha na fila da fleet: " + code;
}
