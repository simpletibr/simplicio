export interface DiffHunk {
  header: string;
  lines: string[];
}

export interface DiffFile {
  path: string;
  additions: number;
  deletions: number;
  hunks: DiffHunk[];
}

export interface ReviewDigest {
  schema: "simplicio.desktop-review/v1";
  repo: string;
  base: string | null;
  status: string;
  diff: string;
  digest: string;
  truncated: boolean;
}

export type AutoMergeReason =
  | "eligible"
  | "plan_digest_missing"
  | "plan_digest_mismatch"
  | "protected_path"
  | "truncated";

export interface AutoMergeEligibility {
  eligible: boolean;
  reason: AutoMergeReason;
}

export interface ReviewView {
  files: DiffFile[];
  additions: number;
  deletions: number;
  flags: ReviewFlag[];
  autoMerge: AutoMergeEligibility;
}

export interface ReviewFlag {
  path: string;
  kind: "protected" | "generated" | "binary";
}

/** Receipt returned by the native inbox write. It is not an agent receipt. */
export interface ReviewSubmissionReceipt {
  schema: "simplicio.review-receipt/v1";
  receipt_id: string;
  path: string;
  entry_digest: string;
  digest: string;
  comments_digest: string;
  comments_bytes: number;
  plan_digest: string | null;
  auto_merge: AutoMergeEligibility;
  idempotent: boolean;
  redacted: true;
}

export type CommitStatus = "committed" | "commit_failed";
export type CommitPhase = "ready" | "committed" | "pushed" | "failed";

/**
 * Receipt of one commit created from the review. `sha` is the real commit id
 * recorded by the native side; on `commit_failed` it stays null and `stderr`
 * carries what git actually wrote.
 */
export interface ReviewCommitReceipt {
  schema: "simplicio.desktop-review-commit/v1";
  status: CommitStatus;
  receipt_id: string | null;
  path: string | null;
  digest: string;
  sha: string | null;
  branch: string;
  paths: string[];
  message_chars: number;
  message_digest: string;
  upstream: string | null;
  pushed: boolean;
  phase: CommitPhase;
  code: string | null;
  stderr: string | null;
  redacted: true;
}

export type PushStatus = "pushed" | "push_failed";

export interface ReviewPushReceipt {
  schema: "simplicio.desktop-review-push/v1";
  status: PushStatus;
  sha: string;
  branch: string;
  upstream: string | null;
  idempotent: boolean;
  code: string | null;
  stderr: string | null;
  redacted: true;
}

/** Why the review cannot be committed. `null` means the commit is offered. */
export type CommitGuard = "truncated" | "protected_path" | "no_changes";

export function commitGuard(view: ReviewView, truncated = false): CommitGuard | null {
  if (truncated) return "truncated";
  if (view.flags.some((flag) => flag.kind === "protected")) return "protected_path";
  if (view.files.length === 0) return "no_changes";
  return null;
}

export function commitGuardLabel(guard: CommitGuard | null): string {
  if (guard === "no_changes") return "Sem mudanças para commitar.";
  if (guard === "protected_path") return "Diff com path protegido: commit e push bloqueados.";
  if (guard === "truncated") return "Diff truncado: commit bloqueado.";
  return "Commit disponível para os arquivos revisados.";
}

export const MAX_COMMIT_MESSAGE_CHARS = 4_096;

/** The message is the user's; only trim/empty/length are enforced here too. */
export function commitMessageError(message: string): "review_message_empty" | "review_message_too_large" | null {
  const trimmed = message.trim();
  if (!trimmed) return "review_message_empty";
  if (trimmed.length > MAX_COMMIT_MESSAGE_CHARS) return "review_message_too_large";
  return null;
}

const COMMIT_PHASES: CommitPhase[] = ["ready", "committed", "pushed", "failed"];
const COMMIT_STATUSES: CommitStatus[] = ["committed", "commit_failed"];
const PUSH_STATUSES: PushStatus[] = ["pushed", "push_failed"];

function commitSha(value: unknown): value is string {
  return typeof value === "string" && /^[0-9a-f]{40}([0-9a-f]{0,24})$/.test(value);
}

function optionalString(value: unknown): value is string | null {
  return value === null || value === undefined || typeof value === "string";
}

export function parseReviewCommitReceipt(value: unknown): ReviewCommitReceipt {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("review_commit_receipt_invalid");
  const raw = value as Record<string, unknown>;
  const paths = raw.paths;
  if (
    raw.schema !== "simplicio.desktop-review-commit/v1" ||
    !COMMIT_STATUSES.includes(raw.status as CommitStatus) ||
    typeof raw.digest !== "string" ||
    typeof raw.branch !== "string" ||
    !Array.isArray(paths) ||
    !paths.every((path) => typeof path === "string") ||
    typeof raw.message_chars !== "number" ||
    typeof raw.message_digest !== "string" ||
    typeof raw.pushed !== "boolean" ||
    !COMMIT_PHASES.includes(raw.phase as CommitPhase) ||
    !optionalString(raw.receipt_id) ||
    !optionalString(raw.path) ||
    !optionalString(raw.upstream) ||
    !optionalString(raw.code) ||
    !optionalString(raw.stderr) ||
    raw.redacted !== true
  ) {
    throw new Error("review_commit_receipt_invalid");
  }
  const sha = raw.sha;
  if (sha !== null && !commitSha(sha)) throw new Error("review_commit_receipt_invalid");
  // A receipt that claims success must carry both the sha and the file it was
  // written to; a failure never pretends to have one.
  if (raw.status === "committed" && (sha === null || typeof raw.path !== "string" || raw.path === "")) {
    throw new Error("review_commit_receipt_invalid");
  }
  return {
    schema: "simplicio.desktop-review-commit/v1",
    status: raw.status as CommitStatus,
    receipt_id: (raw.receipt_id as string | null) ?? null,
    path: (raw.path as string | null) ?? null,
    digest: raw.digest,
    sha: (sha as string | null) ?? null,
    branch: raw.branch,
    paths: paths as string[],
    message_chars: raw.message_chars,
    message_digest: raw.message_digest,
    upstream: (raw.upstream as string | null) ?? null,
    pushed: raw.pushed,
    phase: raw.phase as CommitPhase,
    code: (raw.code as string | null) ?? null,
    stderr: (raw.stderr as string | null) ?? null,
    redacted: true,
  };
}

export function parseReviewPushReceipt(value: unknown): ReviewPushReceipt {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("review_push_receipt_invalid");
  const raw = value as Record<string, unknown>;
  if (
    raw.schema !== "simplicio.desktop-review-push/v1" ||
    !PUSH_STATUSES.includes(raw.status as PushStatus) ||
    !commitSha(raw.sha) ||
    typeof raw.branch !== "string" ||
    typeof raw.idempotent !== "boolean" ||
    !optionalString(raw.upstream) ||
    !optionalString(raw.code) ||
    !optionalString(raw.stderr) ||
    raw.redacted !== true
  ) {
    throw new Error("review_push_receipt_invalid");
  }
  if (raw.status === "pushed" && (typeof raw.upstream !== "string" || raw.upstream.trim() === "")) {
    throw new Error("review_push_receipt_invalid");
  }
  return {
    schema: "simplicio.desktop-review-push/v1",
    status: raw.status as PushStatus,
    sha: raw.sha,
    branch: raw.branch,
    upstream: (raw.upstream as string | null) ?? null,
    idempotent: raw.idempotent,
    code: (raw.code as string | null) ?? null,
    stderr: (raw.stderr as string | null) ?? null,
    redacted: true,
  };
}


const PROTECTED = [
  /(^|\/)Cargo\.toml$/,
  /(^|\/)Cargo\.lock$/,
  /(^|\/)package-lock\.json$/,
  /(^|\/)install\.(sh|ps1)$/,
  /(^|\/)simplicio-update-manifest\.json$/,
  /(^|\/)SHA256SUMS$/,
  /(^|\/)\.github\//,
  /(^|\/)schemas\//,
  /(^|\/)migrations\//,
];
const GENERATED = [/\.generated\./, /(^|\/)dist\//, /(^|\/)target\//];
const REASONS: AutoMergeReason[] = [
  "eligible",
  "plan_digest_missing",
  "plan_digest_mismatch",
  "protected_path",
  "truncated",
];

export function parseUnifiedDiff(text: string): DiffFile[] {
  const files: DiffFile[] = [];
  let current: DiffFile | null = null;
  let hunk: DiffHunk | null = null;
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("diff --git ")) {
      const match = line.match(/ b\/(.+)$/);
      current = { path: match ? match[1] : line.slice(11), additions: 0, deletions: 0, hunks: [] };
      files.push(current);
      hunk = null;
      continue;
    }
    if (!current) continue;
    if (line.startsWith("+++ ") || line.startsWith("--- ") || line.startsWith("index ")) continue;
    if (line.startsWith("@@")) {
      hunk = { header: line, lines: [] };
      current.hunks.push(hunk);
      continue;
    }
    if (line.startsWith("+")) {
      current.additions += 1;
      hunk?.lines.push(line);
      continue;
    }
    if (line.startsWith("-")) {
      current.deletions += 1;
      hunk?.lines.push(line);
      continue;
    }
    hunk?.lines.push(line);
  }
  return files;
}

export function reviewFlags(files: DiffFile[]): ReviewFlag[] {
  const flags: ReviewFlag[] = [];
  for (const file of files) {
    if (PROTECTED.some((pattern) => pattern.test(file.path))) flags.push({ path: file.path, kind: "protected" });
    else if (GENERATED.some((pattern) => pattern.test(file.path))) flags.push({ path: file.path, kind: "generated" });
  }
  return flags;
}

/**
 * Plan-lane eligibility cannot be claimed without a matching plan digest.
 * The native submit writes the same precedence into the receipt.
 */
export function reviewView(digest: ReviewDigest, planDigest?: string | null): ReviewView {
  const files = parseUnifiedDiff(digest.diff);
  const flags = reviewFlags(files);
  const additions = files.reduce((sum, file) => sum + file.additions, 0);
  const deletions = files.reduce((sum, file) => sum + file.deletions, 0);
  const autoMerge = autoMergeEligibility(digest, flags, planDigest ?? null);
  return { files, additions, deletions, flags, autoMerge };
}

function autoMergeEligibility(
  digest: ReviewDigest,
  flags: ReviewFlag[],
  planDigest: string | null,
): AutoMergeEligibility {
  if (digest.truncated) return { eligible: false, reason: "truncated" };
  if (flags.some((flag) => flag.kind === "protected")) return { eligible: false, reason: "protected_path" };
  const plan = planDigest?.trim();
  if (!plan) return { eligible: false, reason: "plan_digest_missing" };
  if (plan.toLowerCase() !== digest.digest.trim().toLowerCase()) {
    return { eligible: false, reason: "plan_digest_mismatch" };
  }
  return { eligible: true, reason: "eligible" };
}

export function autoMergeLabel(eligibility: AutoMergeEligibility): string {
  return eligibility.eligible ? "auto-merge elegível" : "auto-merge: " + eligibility.reason;
}

export function parseReviewReceipt(value: unknown): ReviewSubmissionReceipt {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("review_receipt_invalid");
  const raw = value as Record<string, unknown>;
  const auto = raw.auto_merge as Record<string, unknown> | null | undefined;
  if (
    raw.schema !== "simplicio.review-receipt/v1" ||
    typeof raw.receipt_id !== "string" ||
    typeof raw.path !== "string" ||
    typeof raw.entry_digest !== "string" ||
    typeof raw.digest !== "string" ||
    typeof raw.comments_digest !== "string" ||
    typeof raw.comments_bytes !== "number" ||
    typeof raw.idempotent !== "boolean" ||
    raw.redacted !== true ||
    !auto ||
    typeof auto.eligible !== "boolean" ||
    !REASONS.includes(auto.reason as AutoMergeReason) ||
    auto.eligible !== (auto.reason === "eligible")
  ) {
    throw new Error("review_receipt_invalid");
  }
  const planDigest = raw.plan_digest;
  if (planDigest !== null && typeof planDigest !== "string") throw new Error("review_receipt_invalid");
  return {
    schema: "simplicio.review-receipt/v1",
    receipt_id: raw.receipt_id,
    path: raw.path,
    entry_digest: raw.entry_digest,
    digest: raw.digest,
    comments_digest: raw.comments_digest,
    comments_bytes: raw.comments_bytes,
    plan_digest: planDigest,
    auto_merge: { eligible: auto.eligible, reason: auto.reason as AutoMergeReason },
    idempotent: raw.idempotent,
    redacted: true,
  };
}

export function reviewErrorMessage(code: string): string {
  if (code === "preview_no_runtime") return "Abra o app desktop para revisar diffs; a prévia não lê o repositório.";
  if (code === "review_unavailable") return "O diff do repositório não está disponível.";
  if (code === "review_base_invalid") return "A base informada não é uma revisão válida.";
  if (code === "review_digest_invalid") return "O digest do diff é inválido; recarregue a revisão.";
  if (code === "review_digest_mismatch") return "O diff mudou desde que foi carregado; recarregue antes de enviar.";
  if (code === "review_comments_empty") return "Escreva ao menos um comentário.";
  if (code === "review_comments_too_large") return "Os comentários excedem 20.000 caracteres.";
  if (code === "review_inbox_unavailable") return "Não foi possível gravar o inbox de revisão do repositório.";
  if (code === "review_receipt_invalid") return "O recibo do inbox veio em formato inesperado.";
  if (code === "review_truncated") return "Diff truncado em 200 KB: o commit é recusado porque a revisão está incompleta.";
  if (code === "review_protected_path") return "O diff inclui um path protegido; commit e push ficam bloqueados.";
  if (code === "review_changes_empty") return "Não há mudanças no working tree para commitar.";
  if (code === "review_path_invalid") return "O diff contém um caminho inválido; recarregue a revisão.";
  if (code === "review_message_empty") return "Escreva a mensagem do commit.";
  if (code === "review_message_too_large") return "A mensagem do commit excede 4.096 caracteres.";
  if (code === "review_branch_protected") return "A worktree está em main/master; crie uma branch explícita antes de commitar.";
  if (code === "review_branch_detached") return "A worktree está com HEAD destacado; entre numa branch antes de commitar.";
  if (code === "review_branch_unavailable") return "Não foi possível ler a branch atual da worktree.";
  if (code === "review_commit_base_unsupported") return "Commit exige a revisão sem base: só o working tree é commitado.";
  if (code === "review_commit_in_progress") return "Há merge, rebase ou cherry-pick em andamento; termine antes de commitar.";
  if (code === "review_commit_missing") return "Nenhum commit registrado para esta revisão; commite antes de fazer push.";
  if (code === "review_commit_not_head") return "O HEAD mudou depois do commit registrado; commite de novo antes do push.";
  if (code === "review_commit_branch_changed") return "A branch mudou depois do commit registrado; commite de novo.";
  if (code === "review_commit_sha_invalid") return "O sha informado não é um commit id válido.";
  if (code === "review_commit_receipt_invalid") return "O recibo do commit veio em formato inesperado.";
  if (code === "review_push_no_upstream") return "A branch não tem upstream; marque a criação do upstream para fazer push.";
  if (code === "review_push_upstream_mismatch") return "O upstream aponta para outra branch; o push não é feito sem decisão explícita.";
  return "Falha na revisão: " + code;
}
