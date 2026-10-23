export const DESKTOP_CATALOG_SCHEMA = "simplicio.desktop-catalog/v1" as const;

export type CatalogFieldType = "string" | "number" | "boolean";

export interface CatalogField {
  name: string;
  type: CatalogFieldType;
  description: string;
  required: boolean;
}

export interface CatalogEntry {
  id: string;
  owningPlugin: string;
  tier: string;
  cliSyntax: string;
  mcpToolName: string | null;
  description: string;
  effectClass: string;
  capabilities: string[];
  availability: string;
  version: string;
  changelogExcerpt: string;
  fields: CatalogField[];
}

export interface DesktopCatalog {
  schema: typeof DESKTOP_CATALOG_SCHEMA;
  version: string;
  digest: string | null;
  entries: CatalogEntry[];
}

const ID = /^[a-z0-9][a-z0-9-]{0,63}$/;
const MAX_ENTRIES = 512;

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("catalog_invalid");
  return value as Record<string, unknown>;
}

function text(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  if (typeof value !== "string" || value.length > 2000) throw new Error("catalog_invalid");
  return value;
}

function fieldsOf(value: unknown): CatalogField[] {
  const schema = record(value);
  const properties = schema.properties === undefined ? {} : record(schema.properties);
  const required = Array.isArray(schema.required) ? new Set(schema.required.filter((item): item is string => typeof item === "string")) : new Set<string>();
  const fields: CatalogField[] = [];
  for (const [name, raw] of Object.entries(properties)) {
    if (fields.length >= 32 || !/^[a-z0-9_-]{1,64}$/i.test(name)) continue;
    const property = record(raw);
    const type = property.type;
    if (type !== "string" && type !== "number" && type !== "integer" && type !== "boolean") continue;
    fields.push({
      name,
      type: type === "integer" ? "number" : type,
      description: text(property.description),
      required: required.has(name),
    });
  }
  return fields;
}

function entryOf(value: unknown): CatalogEntry {
  const raw = record(value);
  const id = text(raw.id);
  if (!ID.test(id)) throw new Error("catalog_invalid");
  const capabilities = Array.isArray(raw.capabilities_requiring_consent)
    ? raw.capabilities_requiring_consent.filter((item): item is string => typeof item === "string").slice(0, 16)
    : [];
  return {
    id,
    owningPlugin: text(raw.owning_plugin, "unknown"),
    tier: text(raw.tier, "kernel"),
    cliSyntax: text(raw.cli_syntax, "simplicio " + id),
    mcpToolName: raw.mcp_tool_name === null || raw.mcp_tool_name === undefined ? null : text(raw.mcp_tool_name),
    description: text(raw.description),
    effectClass: text(raw.effect_class, "read_only"),
    capabilities,
    availability: text(raw.availability, "installed"),
    version: text(raw.version, "unknown"),
    changelogExcerpt: text(raw.changelog_excerpt),
    fields: fieldsOf(raw.args_schema),
  };
}

/** Parse the Runtime desktop catalog; every entry must be renderable. */
export function parseDesktopCatalog(value: unknown): DesktopCatalog {
  const raw = record(value);
  if (raw.schema !== DESKTOP_CATALOG_SCHEMA) throw new Error("catalog_invalid");
  if (!Array.isArray(raw.entries) || raw.entries.length > MAX_ENTRIES) throw new Error("catalog_invalid");
  const entries = raw.entries.map(entryOf);
  if (new Set(entries.map((entry) => entry.id)).size !== entries.length) throw new Error("catalog_invalid");
  return {
    schema: DESKTOP_CATALOG_SCHEMA,
    version: text(raw.version, "unknown"),
    digest: raw.digest_sha256 === null || raw.digest_sha256 === undefined ? null : text(raw.digest_sha256),
    entries,
  };
}

export function filterCatalog(entries: CatalogEntry[], query: string): CatalogEntry[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return entries.slice(0, 50);
  return entries
    .filter((entry) => [entry.id, entry.cliSyntax, entry.description, entry.owningPlugin, entry.mcpToolName ?? ""]
      .some((value) => value.toLowerCase().includes(needle)))
    .slice(0, 50);
}

export type CatalogValues = Record<string, string | number | boolean>;

/** Build the equivalent CLI invocation; only catalog-declared fields are accepted. */
export function buildCatalogArgs(entry: CatalogEntry, values: CatalogValues): string[] {
  const argv: string[] = [entry.id];
  for (const field of entry.fields) {
    const value = values[field.name];
    if (value === undefined || value === "") {
      if (field.required) throw new Error("catalog_field_required:" + field.name);
      continue;
    }
    if (field.type === "boolean") {
      if (typeof value !== "boolean") throw new Error("catalog_field_invalid:" + field.name);
      if (value) argv.push("--" + field.name);
      continue;
    }
    if (field.type === "number") {
      const number = typeof value === "number" ? value : Number(value);
      if (!Number.isFinite(number)) throw new Error("catalog_field_invalid:" + field.name);
      argv.push("--" + field.name, String(number));
      continue;
    }
    if (typeof value !== "string") throw new Error("catalog_field_invalid:" + field.name);
    argv.push("--" + field.name, value);
  }
  argv.push("--json");
  return argv;
}

export function catalogCliLine(entry: CatalogEntry, values: CatalogValues = {}): string {
  try {
    return "simplicio " + buildCatalogArgs(entry, values).join(" ");
  } catch {
    return entry.cliSyntax;
  }
}

export function entryRequiresConsent(entry: CatalogEntry): boolean {
  return entry.capabilities.length > 0;
}
