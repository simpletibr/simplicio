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

export interface ReviewView {
  files: DiffFile[];
  additions: number;
  deletions: number;
  flags: ReviewFlag[];
  autoMerge: { eligible: boolean; reason: string };
}

export interface ReviewFlag {
  path: string;
  kind: "protected" | "generated" | "binary";
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

/** Plan-lane eligibility cannot be claimed without a matching plan digest. */
export function reviewView(digest: ReviewDigest): ReviewView {
  const files = parseUnifiedDiff(digest.diff);
  const flags = reviewFlags(files);
  const additions = files.reduce((sum, file) => sum + file.additions, 0);
  const deletions = files.reduce((sum, file) => sum + file.deletions, 0);
  const autoMerge = flags.some((flag) => flag.kind === "protected")
    ? { eligible: false, reason: "protected_path" }
    : { eligible: false, reason: "plan_digest_not_provided" };
  return { files, additions, deletions, flags, autoMerge };
}

export function reviewErrorMessage(code: string): string {
  if (code === "preview_no_runtime") return "Abra o app desktop para revisar diffs; a prévia não lê o repositório.";
  if (code === "review_unavailable") return "O diff do repositório não está disponível.";
  return "Falha na revisão: " + code;
}
