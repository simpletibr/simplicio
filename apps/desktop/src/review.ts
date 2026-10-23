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
  return "Falha na revisão: " + code;
}
