export interface Worktree {
  path: string;
  head: string | null;
  branch: string | null;
  detached: boolean;
  bare: boolean;
  main: boolean;
  issue: number | null;
}

export interface FleetState {
  worktrees: Worktree[];
  active: number;
  wipLimit: number;
  overLimit: boolean;
}

export const DEFAULT_WIP_LIMIT = 5;

/** Parse `git worktree list --porcelain`; the first block is the main checkout. */
export function parseWorktrees(text: string): Worktree[] {
  const blocks = text.trim().split(/\r?\n\r?\n/).filter(Boolean);
  return blocks.map((block, index) => {
    const fields = new Map<string, string>();
    for (const line of block.split(/\r?\n/)) {
      const space = line.indexOf(" ");
      if (space > 0) fields.set(line.slice(0, space), line.slice(space + 1));
    }
    const path = fields.get("worktree");
    if (!path) throw new Error("worktree_parse_invalid");
    const branchRef = fields.get("branch") ?? null;
    const branch = branchRef ? branchRef.replace(/^refs\/heads\//, "") : null;
    return {
      path,
      head: fields.get("HEAD") ?? null,
      branch,
      detached: fields.has("detached"),
      bare: fields.has("bare"),
      main: index === 0,
      issue: branch ? issueFromBranch(branch) : null,
    };
  });
}

export function issueFromBranch(branch: string): number | null {
  const match = branch.match(/(?:^|\/)issue-(\d+)$/);
  if (!match) return null;
  const issue = Number(match[1]);
  return Number.isSafeInteger(issue) && issue > 0 ? issue : null;
}

export function fleetState(worktrees: Worktree[], wipLimit = DEFAULT_WIP_LIMIT): FleetState {
  if (!Number.isSafeInteger(wipLimit) || wipLimit < 1 || wipLimit > 64) throw new Error("wip_limit_invalid");
  const active = worktrees.filter((item) => !item.main && !item.bare).length;
  return { worktrees, active, wipLimit, overLimit: active >= wipLimit };
}

export function createAllowed(state: FleetState): boolean {
  return !state.overLimit;
}

export function fleetErrorMessage(code: string): string {
  if (code === "wip_limit_reached") return "Limite de WIP atingido; finalize uma tarefa antes de criar outra.";
  if (code === "worktree_create_failed") return "Não foi possível criar o worktree; verifique o repositório e a issue.";
  if (code === "preview_no_runtime") return "Abra o app desktop para criar worktrees; a prévia não altera o repositório.";
  return "Falha na operação de worktree: " + code;
}
