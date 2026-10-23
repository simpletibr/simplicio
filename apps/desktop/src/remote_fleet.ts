/**
 * `simplicio.desktop-remotes/v1` is a user-authored allowlist of Simplicio
 * runtimes on other machines. The file never carries a credential: it names an
 * environment variable and the native command resolves it in-process.
 *
 * `simplicio.desktop-remote-fleet/v1` is the bounded, redacted projection this
 * module accepts back from the Desktop bridge. Nothing here opens a socket;
 * the native command owns transport, timeouts and authorization.
 */

export const REMOTE_CONFIG_SCHEMA = "simplicio.desktop-remotes/v1";
export const REMOTE_FLEET_SCHEMA = "simplicio.desktop-remote-fleet/v1";
export const MAX_REMOTE_FLEET = 32;
export const MAX_REMOTE_LABEL = 80;
export const MAX_REMOTE_URL = 2048;
export const MAX_REMOTE_LATENCY_MS = 60_000;

const REMOTE_ID = /^[a-z0-9][a-z0-9._-]{0,63}$/;
const TOKEN_ENV = /^[A-Z_][A-Z0-9_]{0,127}$/;
const REASON_CODE = /^[a-z0-9][a-z0-9_]{0,63}$/;
const SECRET_VALUE = /(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{10,})/;

export type RemoteStatus = "unknown" | "online" | "offline" | "unauthorized";

export interface RemoteConfigEntry {
  id: string;
  label: string;
  /** Normalized http(s) base URL without credentials, query or fragment. */
  url: string;
  /** Environment variable that holds the bearer token, never the token itself. */
  tokenEnv: string | null;
}

export interface RemoteConfig {
  schema: typeof REMOTE_CONFIG_SCHEMA;
  remotes: RemoteConfigEntry[];
}

export interface RemoteMachine {
  id: string;
  label: string;
  url: string;
  status: RemoteStatus;
  /** True only when this Desktop sent a token and the remote accepted it. */
  authenticated: boolean;
  version: string | null;
  latencyMs: number | null;
  reasonCode: string | null;
}

export interface RemoteFleet {
  schema: typeof REMOTE_FLEET_SCHEMA;
  configured: boolean;
  remotes: RemoteMachine[];
  error: string | null;
  observedAt: number | null;
}

export interface RemoteHealthObservation {
  status: RemoteStatus;
  authenticated: boolean;
  version: string | null;
  reasonCode: string | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasControl(value: string): boolean {
  return /[\u0000-\u001f\u007f]/.test(value);
}

/** Rejects a value that looks like a credential, so it cannot be persisted by mistake. */
export function containsInlineSecret(value: string): boolean {
  return SECRET_VALUE.test(value);
}

/** Redacts credentials and control characters from diagnostics before rendering them. */
export function redactRemoteText(value: string): string {
  return value
    .replace(/Bearer\s+[^\s"']+/gi, "Bearer [redacted]")
    .replace(/((?:token|secret|password|api[_-]?key)\s*[=:]\s*)[^\s"',;]+/gi, "$1[redacted]")
    .replace(new RegExp(SECRET_VALUE.source, "g"), "[redacted]")
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .trim()
    .slice(0, 240);
}

export function isLoopbackRemoteUrl(value: string): boolean {
  let host: string;
  try {
    host = new URL(value).hostname.replace(/^\[|\]$/g, "");
  } catch {
    return false;
  }
  return host === "localhost" || host === "::1" || /^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(host);
}

/** Normalizes an allowlisted base URL; credentials, query and fragment are denied. */
export function normalizeRemoteUrl(value: unknown): string {
  if (typeof value !== "string" || !value.trim() || value.length > MAX_REMOTE_URL) {
    throw new Error("remote_config_url_invalid");
  }
  if (containsInlineSecret(value)) throw new Error("remote_secret_inline");
  let url: URL;
  try {
    url = new URL(value.trim());
  } catch {
    throw new Error("remote_config_url_invalid");
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") throw new Error("remote_config_url_insecure");
  if (url.username || url.password) throw new Error("remote_config_url_credentials");
  if (url.search || url.hash) throw new Error("remote_config_url_invalid");
  if (!url.hostname) throw new Error("remote_config_url_invalid");
  return url.origin + url.pathname.replace(/\/+$/, "");
}

function parseLabel(value: unknown): string {
  if (typeof value !== "string") throw new Error("remote_config_label_invalid");
  const label = value.trim();
  if (!label || label.length > MAX_REMOTE_LABEL || hasControl(label) || containsInlineSecret(label)) {
    throw new Error("remote_config_label_invalid");
  }
  return label;
}

function parseId(value: unknown): string {
  if (typeof value !== "string" || !REMOTE_ID.test(value)) throw new Error("remote_config_id_invalid");
  return value;
}

function parseTokenEnv(value: unknown): string | null {
  if (value === undefined || value === null) return null;
  if (typeof value !== "string" || !TOKEN_ENV.test(value)) throw new Error("remote_config_token_env_invalid");
  return value;
}

/**
 * Strict parser for the on-disk contract. Unknown fields are rejected so a
 * `token` key can never be smuggled into the file, and a non-loopback remote
 * is denied unless it names a token environment variable.
 */
export function parseRemoteConfig(value: unknown): RemoteConfig {
  if (!isRecord(value)) throw new Error("remote_config_invalid");
  if (Object.keys(value).some((key) => key !== "schema" && key !== "remotes")) {
    throw new Error("remote_config_unknown_field");
  }
  if (value.schema !== REMOTE_CONFIG_SCHEMA) throw new Error("remote_config_schema");
  if (!Array.isArray(value.remotes)) throw new Error("remote_config_invalid");
  if (value.remotes.length > MAX_REMOTE_FLEET) throw new Error("remote_config_limit");
  const ids = new Set<string>();
  const remotes = value.remotes.map((entry): RemoteConfigEntry => {
    if (!isRecord(entry)) throw new Error("remote_config_invalid");
    if (Object.keys(entry).some((key) => !["id", "label", "url", "token_env"].includes(key))) {
      throw new Error("remote_config_unknown_field");
    }
    const id = parseId(entry.id);
    if (ids.has(id)) throw new Error("remote_config_duplicate");
    ids.add(id);
    const url = normalizeRemoteUrl(entry.url);
    const tokenEnv = parseTokenEnv(entry.token_env);
    if (!isLoopbackRemoteUrl(url) && tokenEnv === null) throw new Error("remote_config_token_required");
    return { id, label: parseLabel(entry.label), url, tokenEnv };
  });
  return { schema: REMOTE_CONFIG_SCHEMA, remotes };
}

const STATUSES: readonly RemoteStatus[] = ["unknown", "online", "offline", "unauthorized"];

function parseStatus(value: unknown): RemoteStatus {
  if (typeof value !== "string" || !STATUSES.includes(value as RemoteStatus)) {
    throw new Error("remote_fleet_status_invalid");
  }
  return value as RemoteStatus;
}

function parseReason(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value !== "string" || !REASON_CODE.test(value)) throw new Error("remote_fleet_reason_invalid");
  return value;
}

function parseVersion(value: unknown): string | null {
  if (value === null || value === undefined) return null;
  if (typeof value !== "string") throw new Error("remote_fleet_version_invalid");
  const version = value.trim();
  if (!version || version.length > 64 || hasControl(version)) throw new Error("remote_fleet_version_invalid");
  return version;
}

function parseLatency(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  if (!Number.isSafeInteger(value) || (value as number) < 0 || (value as number) > MAX_REMOTE_LATENCY_MS) {
    throw new Error("remote_fleet_latency_invalid");
  }
  return value as number;
}

/** Strict parser for the native projection; it never accepts an unredacted payload. */
export function parseRemoteFleet(value: unknown): RemoteFleet {
  if (!isRecord(value)) throw new Error("remote_fleet_invalid");
  if (value.schema !== REMOTE_FLEET_SCHEMA) throw new Error("remote_fleet_schema");
  if (value.redacted !== true) throw new Error("remote_fleet_unredacted");
  if (typeof value.configured !== "boolean") throw new Error("remote_fleet_invalid");
  if (!Array.isArray(value.remotes)) throw new Error("remote_fleet_invalid");
  if (value.remotes.length > MAX_REMOTE_FLEET) throw new Error("remote_fleet_limit");
  const error = parseReason(value.error);
  const observedAt = value.observedAt === null || value.observedAt === undefined
    ? null
    : Number.isSafeInteger(value.observedAt) && (value.observedAt as number) > 0
      ? (value.observedAt as number)
      : (() => { throw new Error("remote_fleet_observed_at_invalid"); })();
  const remotes = value.remotes.map((entry): RemoteMachine => {
    if (!isRecord(entry)) throw new Error("remote_fleet_invalid");
    if (Object.keys(entry).some((key) => ![
      "id", "label", "url", "status", "authenticated", "version", "latencyMs", "reasonCode",
    ].includes(key))) {
      throw new Error("remote_fleet_unknown_field");
    }
    if (typeof entry.authenticated !== "boolean") throw new Error("remote_fleet_invalid");
    const status = parseStatus(entry.status);
    if (status === "unauthorized" && entry.authenticated) throw new Error("remote_fleet_invalid");
    return {
      id: parseId(entry.id),
      label: parseLabel(entry.label),
      url: normalizeRemoteUrl(entry.url),
      status,
      authenticated: entry.authenticated,
      version: parseVersion(entry.version),
      latencyMs: parseLatency(entry.latencyMs),
      reasonCode: parseReason(entry.reasonCode),
    };
  });
  return { schema: REMOTE_FLEET_SCHEMA, configured: value.configured, remotes, error, observedAt };
}

/** Status mapping shared with the native probe; a 2xx only authenticates when a token was sent. */
export function classifyRemoteHealth(
  httpStatus: number,
  body: unknown,
  sentToken: boolean,
): RemoteHealthObservation {
  if (httpStatus === 401 || httpStatus === 403) {
    return { status: "unauthorized", authenticated: false, version: null, reasonCode: "remote_unauthorized" };
  }
  if (!Number.isInteger(httpStatus) || httpStatus < 200 || httpStatus > 299) {
    return { status: "offline", authenticated: false, version: null, reasonCode: "remote_http_error" };
  }
  const state = isRecord(body) ? body.status : undefined;
  if (state !== "ok" && state !== "healthy") {
    return { status: "offline", authenticated: false, version: null, reasonCode: "remote_health_invalid" };
  }
  const rawVersion = isRecord(body) ? body.version : null;
  const version = typeof rawVersion === "string" && rawVersion.trim() && rawVersion.length <= 64 && !hasControl(rawVersion)
    ? rawVersion.trim()
    : null;
  return { status: "online", authenticated: sentToken, version, reasonCode: null };
}

export const REMOTE_STATUS_LABELS: Record<RemoteStatus, string> = {
  unknown: "Não consultado",
  online: "Online",
  offline: "Offline",
  unauthorized: "Não autorizado",
};

export function canActOnRemote(remote: RemoteMachine): boolean {
  return remote.status === "online" && remote.authenticated;
}

/** A missing reason means the action is allowed; otherwise it is the UI restriction. */
export function remoteActionBlocker(remote: RemoteMachine): string | null {
  if (remote.status === "offline") return "A máquina está offline; nenhuma ação remota foi enviada.";
  if (remote.status === "unauthorized") return "A máquina recusou ou não recebeu autorização.";
  if (remote.status === "unknown") return "O estado da máquina ainda não foi consultado.";
  if (!remote.authenticated) return "Sem token autorizado para esta máquina.";
  return null;
}

export interface RemoteFleetSummary {
  total: number;
  online: number;
  offline: number;
  unauthorized: number;
  actionable: number;
}

export function summarizeRemoteFleet(remotes: RemoteMachine[]): RemoteFleetSummary {
  return remotes.slice(0, MAX_REMOTE_FLEET).reduce<RemoteFleetSummary>(
    (summary, remote) => {
      summary.total += 1;
      if (remote.status === "online") summary.online += 1;
      else if (remote.status === "offline") summary.offline += 1;
      else if (remote.status === "unauthorized") summary.unauthorized += 1;
      if (canActOnRemote(remote)) summary.actionable += 1;
      return summary;
    },
    { total: 0, online: 0, offline: 0, unauthorized: 0, actionable: 0 },
  );
}

const REMOTE_ERROR_MESSAGES: Record<string, string> = {
  remote_config_unreadable: "Não foi possível ler ~/.simplicio/desktop-remotes.json.",
  remote_config_too_large: "O arquivo de máquinas remotas excede o limite permitido.",
  remote_config_invalid: "O arquivo de máquinas remotas não é um JSON válido.",
  remote_config_schema: "O schema do arquivo de máquinas remotas não é compatível.",
  remote_config_unknown_field: "O arquivo contém um campo não permitido; tokens não podem ser gravados nele.",
  remote_config_limit: "O arquivo excede o limite de 32 máquinas remotas.",
  remote_config_duplicate: "O arquivo repete o identificador de uma máquina remota.",
  remote_config_id_invalid: "Um identificador de máquina remota é inválido.",
  remote_config_label_invalid: "Um rótulo de máquina remota é inválido.",
  remote_config_url_invalid: "Uma URL de máquina remota é inválida.",
  remote_config_url_insecure: "Somente URLs http(s) são aceitas.",
  remote_config_url_credentials: "A URL não pode embutir credenciais.",
  remote_config_token_required: "Uma máquina fora do loopback exige token_env.",
  remote_config_token_env_invalid: "token_env deve ser um nome de variável de ambiente.",
  remote_secret_inline: "O arquivo parece conter um token literal; use token_env.",
  remote_fleet_timeout: "A consulta da frota remota excedeu o tempo limite.",
  preview_no_runtime: "Prévia visual: a frota remota não foi consultada.",
};

export function remoteFleetErrorMessage(code: string): string {
  return REMOTE_ERROR_MESSAGES[code] ?? "Falha na frota remota: " + redactRemoteText(code);
}
