/**
 * Worktree orientation contract (#433).
 *
 * The native side measures the first orientation of a worktree from the
 * Runtime's shared default-branch baseline (#6594). This module parses that
 * receipt and is the only place the UI learns a duration: a number exists only
 * when `status === "measured"`, so an unmeasured orientation can never be
 * rendered as a measurement.
 */

export const ORIENTATION_SCHEMA = "simplicio.desktop-worktree-orientation/v1";
export const WORKTREE_CREATE_SCHEMA = "simplicio.desktop-worktree-create/v1";
/** The acceptance budget of #433. */
export const ORIENTATION_BUDGET_MS = 2_000;
const MAX_ORIENTATION_MS = 86_400_000;

export const ORIENTATION_STATUSES = [
  "measured",
  "baseline_missing",
  "stale",
  "timeout",
  "unavailable",
  "map_failed",
  "invalid",
] as const;
export type OrientationStatus = (typeof ORIENTATION_STATUSES)[number];

export type OrientationGeneration = "baseline" | "baseline+delta";

export interface OrientationMeasurement {
  status: OrientationStatus;
  /** Present only for a measured orientation; never synthesized. */
  orientation_ms: number | null;
  generation: OrientationGeneration | null;
  /** True only when the Runtime served the stored baseline (`cache_state: hit`). */
  baseline_reused: boolean;
  /** Derived from the measured number, so a lying payload cannot widen the budget. */
  within_budget: boolean;
  error: string | null;
  hint: string | null;
}

export interface WorktreeCreateReceipt {
  schema: typeof WORKTREE_CREATE_SCHEMA;
  status: string;
  issue: number;
  branch: string;
  path: string;
  orientation: OrientationMeasurement;
}

function record(value: unknown, code: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(code);
  return value as Record<string, unknown>;
}

function optionalString(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function isStatus(value: unknown): value is OrientationStatus {
  return typeof value === "string" && (ORIENTATION_STATUSES as readonly string[]).includes(value);
}

function isGeneration(value: unknown): value is OrientationGeneration {
  return value === "baseline" || value === "baseline+delta";
}

/** Parse one orientation receipt. A failed orientation carrying a number is a contract violation. */
export function parseOrientation(value: unknown): OrientationMeasurement {
  const source = record(value, "orientation_invalid");
  if (source.schema !== ORIENTATION_SCHEMA) throw new Error("orientation_invalid");
  if (!isStatus(source.status)) throw new Error("orientation_invalid");
  const status = source.status;
  if (status === "measured") {
    const measured = source.orientation_ms;
    if (
      typeof measured !== "number" ||
      !Number.isSafeInteger(measured) ||
      measured < 0 ||
      measured > MAX_ORIENTATION_MS
    ) {
      throw new Error("orientation_invalid");
    }
    if (!isGeneration(source.generation)) throw new Error("orientation_invalid");
    if (source.baseline_reused !== true) throw new Error("orientation_invalid");
    return {
      status,
      orientation_ms: measured,
      generation: source.generation,
      baseline_reused: true,
      within_budget: measured < ORIENTATION_BUDGET_MS,
      error: null,
      hint: optionalString(source.hint),
    };
  }
  if (source.orientation_ms !== null && source.orientation_ms !== undefined) {
    throw new Error("orientation_invalid");
  }
  return {
    status,
    orientation_ms: null,
    generation: null,
    baseline_reused: false,
    within_budget: false,
    error: optionalString(source.error),
    hint: optionalString(source.hint),
  };
}

/** Parse the create receipt and keep the orientation that was measured with it. */
export function parseWorktreeCreateReceipt(value: unknown): WorktreeCreateReceipt {
  const source = record(value, "worktree_create_invalid");
  if (source.schema !== WORKTREE_CREATE_SCHEMA) throw new Error("worktree_create_invalid");
  const issue = source.issue;
  if (typeof issue !== "number" || !Number.isSafeInteger(issue) || issue < 1) {
    throw new Error("worktree_create_invalid");
  }
  if (typeof source.path !== "string" || source.path.length === 0) {
    throw new Error("worktree_create_invalid");
  }
  return {
    schema: WORKTREE_CREATE_SCHEMA,
    status: typeof source.status === "string" ? source.status : "created",
    issue,
    branch: typeof source.branch === "string" ? source.branch : "",
    path: source.path,
    orientation: parseOrientation(source.orientation),
  };
}

/** Actionable message for an orientation that produced no number. */export function orientationNotice(measurement: OrientationMeasurement): string | null {
  if (measurement.status === "measured") return null;
  switch (measurement.status) {
    case "baseline_missing":
      return "Baseline ausente para este repositório; rode `simplicio map --repo <repo> --json` no default branch. A orientação não foi medida.";
    case "stale":
      return "O Runtime serviu outra geração do mapa; abra a tarefa de novo. A orientação não foi medida.";
    case "timeout":
      return "A orientação passou do limite de tempo; a tarefa continua válida e pode ser aberta de novo.";
    case "unavailable":
      return "O Runtime não está disponível; a orientação não foi medida.";
    case "map_failed":
      return "O Runtime não devolveu um mapa válido; a orientação não foi medida.";
    default:
      return "A resposta de orientação não pôde ser lida; a orientação não foi medida.";
  }
}

/**
 * Fields a fleet task may take from a measurement. The board renders
 * `orientation_ms` as the real duration and "orientação não medida" without
 * it, so an unmeasured orientation contributes nothing.
 */
export function orientationFields(
  measurement: OrientationMeasurement | null | undefined,
): { orientation_ms?: number } {
  if (!measurement || measurement.status !== "measured" || measurement.orientation_ms === null) {
    return {};
  }
  return { orientation_ms: measurement.orientation_ms };
}
