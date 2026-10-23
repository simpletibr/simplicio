export const CACHE_METER_SCHEMA = "simplicio.cache-meter/v1" as const;

export type CacheBustAttribution =
  | "compaction"
  | "injected_context"
  | "tools_change"
  | "system_prompt_change"
  | "ttl_gap"
  | "model_switch"
  | "unknown";

export interface CacheBust {
  request_index: number;
  expected_read: number;
  actual_read: number;
  attribution: CacheBustAttribution[];
}

export interface CacheRequest {
  index: number;
  model: string | null;
  input: number;
  read: number;
  write: number;
  request_share: number | null;
  cumulative_share: number | null;
  prefix_reuse: number | null;
}

export interface CacheMeterReceipt {
  schema: typeof CACHE_METER_SCHEMA;
  status: "measured" | "unmeasured";
  requests: number;
  session_hit_rate: number | null;
  tolerance_tokens: number;
  ttl_secs: number;
  busts: CacheBust[];
  per_request: CacheRequest[];
}

const ATTRIBUTIONS: CacheBustAttribution[] = [
  "compaction",
  "injected_context",
  "tools_change",
  "system_prompt_change",
  "ttl_gap",
  "model_switch",
  "unknown",
];

const MAX_REQUESTS = 512;
const MAX_BUSTS = 256;

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("cache_meter_invalid");
  }
  return value as Record<string, unknown>;
}

function integer(value: unknown): number {
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) {
    throw new Error("cache_meter_invalid");
  }
  return value;
}

function optionalRatio(value: unknown): number | null {
  if (value === null) return null;
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
    throw new Error("cache_meter_invalid");
  }
  return value;
}

function parseBust(value: unknown): CacheBust {
  const raw = record(value);
  if (!Array.isArray(raw.attribution) || raw.attribution.length === 0) {
    throw new Error("cache_meter_invalid");
  }
  const attribution = raw.attribution.map((item) => {
    if (typeof item !== "string" || !(ATTRIBUTIONS as string[]).includes(item)) {
      throw new Error("cache_meter_invalid");
    }
    return item as CacheBustAttribution;
  });
  return {
    request_index: integer(raw.request_index),
    expected_read: integer(raw.expected_read),
    actual_read: integer(raw.actual_read),
    attribution,
  };
}

function parseRequest(value: unknown): CacheRequest {
  const raw = record(value);
  const model = raw.model === null ? null : raw.model;
  if (model !== null && (typeof model !== "string" || model.length > 256)) {
    throw new Error("cache_meter_invalid");
  }
  return {
    index: integer(raw.index),
    model,
    input: integer(raw.input),
    read: integer(raw.read),
    write: integer(raw.write),
    request_share: optionalRatio(raw.request_share),
    cumulative_share: optionalRatio(raw.cumulative_share),
    prefix_reuse: optionalRatio(raw.prefix_reuse),
  };
}

/** Parse only the Runtime receipt; the renderer never recomputes a hit rate. */
export function parseCacheMeter(value: unknown): CacheMeterReceipt {
  const raw = record(value);
  if (raw.schema !== CACHE_METER_SCHEMA
    || (raw.status !== "measured" && raw.status !== "unmeasured")) {
    throw new Error("cache_meter_invalid");
  }
  const requests = integer(raw.requests);
  const sessionHitRate = optionalRatio(raw.session_hit_rate);
  const ttlSecs = integer(raw.ttl_secs);
  if (!Array.isArray(raw.busts) || raw.busts.length > MAX_BUSTS) throw new Error("cache_meter_invalid");
  if (!Array.isArray(raw.per_request) || raw.per_request.length > MAX_REQUESTS) throw new Error("cache_meter_invalid");
  const busts = raw.busts.map(parseBust);
  const perRequest = raw.per_request.map(parseRequest);
  if (requests !== perRequest.length) throw new Error("cache_meter_invalid");
  if (raw.status === "unmeasured" && sessionHitRate !== null) throw new Error("cache_meter_invalid");
  return {
    schema: CACHE_METER_SCHEMA,
    status: raw.status,
    requests,
    session_hit_rate: sessionHitRate,
    tolerance_tokens: integer(raw.tolerance_tokens),
    ttl_secs: ttlSecs,
    busts,
    per_request: perRequest,
  };
}

/** Tokens billed for the session; zero means no percentage may be shown. */
export function billedInputTokens(receipt: CacheMeterReceipt): number {
  return receipt.per_request.reduce((sum, request) => sum + request.input + request.read + request.write, 0);
}

/**
 * Integer percent while rounding stays below 100%; otherwise add the minimum
 * decimals that keep the displayed value below 100. A true full hit is 100%.
 * Returns null before any input is billed, so an empty session never shows 0%.
 */
export function formatCacheHitRate(rate: number | null, billedInput: number): string | null {
  if (rate === null || billedInput <= 0) return null;
  if (rate >= 1) return "100%";
  const percent = rate * 100;
  let decimals = 0;
  let text = percent.toFixed(decimals);
  while (Number(text) >= 100 && decimals < 4) {
    decimals += 1;
    text = percent.toFixed(decimals);
  }
  return text + "%";
}

export function formatPrefixReuse(rate: number | null): string | null {
  if (rate === null) return null;
  return formatCacheHitRate(rate, 1);
}

const CAUSE_LABELS: Record<CacheBustAttribution, string> = {
  compaction: "compactação",
  injected_context: "contexto injetado",
  tools_change: "mudança de ferramentas",
  system_prompt_change: "mudança de system prompt",
  ttl_gap: "intervalo TTL",
  model_switch: "troca de modelo",
  unknown: "desconhecida",
};

export function cacheBustCauseLabel(cause: CacheBustAttribution): string {
  return CAUSE_LABELS[cause];
}

export function cacheBustCauses(bust: CacheBust): string {
  return bust.attribution.map(cacheBustCauseLabel).join(", ");
}
