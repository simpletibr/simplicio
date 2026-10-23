export const MCP_REGISTER_PLAN_SCHEMA = "simplicio.mcp-register-plan/v1" as const;

export interface HostWrite {
  label: string;
  kind: string;
  path: string;
  profile: string | null;
  mapperOnlyRequired: boolean;
  compliant: boolean;
}

export interface HostsPlan {
  schema: typeof MCP_REGISTER_PLAN_SCHEMA;
  status: string;
  binary: string | null;
  hosts: HostWrite[];
}

const MAPPER_ONLY = new Set(["claude", "claude-code", "claude-desktop", "hermes", "hermes-agent"]);

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("hosts_plan_invalid");
  return value as Record<string, unknown>;
}

function text(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  if (typeof value !== "string" || value.length > 20000) throw new Error("hosts_plan_invalid");
  return value;
}

export function requiresMapperOnly(label: string): boolean {
  return MAPPER_ONLY.has(label.trim().toLowerCase());
}

function profileFromCurrent(current: string): string | null {
  const match = current.match(/"SIMPLICIO_MCP_PROFILE"\s*:\s*"([^"]+)"/);
  return match ? match[1] : null;
}

function writeOf(value: unknown): HostWrite {
  const raw = record(value);
  const label = text(raw.label);
  if (!label || label.length > 128) throw new Error("hosts_plan_invalid");
  const current = text(raw.current);
  const profile = profileFromCurrent(current);
  const required = requiresMapperOnly(label);
  return {
    label,
    kind: text(raw.kind, "unknown"),
    path: text(raw.path),
    profile,
    mapperOnlyRequired: required,
    compliant: !required || profile === null || profile === "mapper-only",
  };
}

/** Parse the Runtime MCP registration plan; the current profile is read from the config body. */
export function parseHostsPlan(value: unknown): HostsPlan {
  const raw = record(value);
  if (raw.schema !== MCP_REGISTER_PLAN_SCHEMA) throw new Error("hosts_plan_invalid");
  if (!Array.isArray(raw.writes) || raw.writes.length > 256) throw new Error("hosts_plan_invalid");
  return {
    schema: MCP_REGISTER_PLAN_SCHEMA,
    status: text(raw.status, "unknown"),
    binary: raw.binary === null || raw.binary === undefined ? null : text(raw.binary),
    hosts: raw.writes.map(writeOf),
  };
}

export function hostStatusLabel(host: HostWrite): string {
  if (!host.compliant) return "perfil divergente";
  return host.kind === "noop" ? "já registrado" : "pronto para registrar";
}
