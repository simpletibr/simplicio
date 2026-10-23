export const PLUGIN_LIST_SCHEMA = "simplicio.plugin-list/v1" as const;

export type PluginTier = "required" | "installed";

export interface PluginEntry {
  name: string;
  version: string;
  status: string;
  reason: string | null;
  commands: string[];
  tools: string[];
  binarySha256: string | null;
  removable: boolean;
  tier: PluginTier;
}

export interface PluginCatalog {
  schema: typeof PLUGIN_LIST_SCHEMA;
  root: string | null;
  plugins: PluginEntry[];
}

const NAME = /^[a-z0-9][a-z0-9._-]{0,127}$/i;
const DANGEROUS = new Set(["simplicio-computer-use", "simplicio-browser-use"]);
const MAX_PLUGINS = 256;
const MAX_LIST = 64;

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("plugin_catalog_invalid");
  return value as Record<string, unknown>;
}

function name(value: unknown): string {
  if (typeof value !== "string" || !NAME.test(value)) throw new Error("plugin_catalog_invalid");
  return value;
}

function text(value: unknown, fallback = ""): string {
  if (value === null || value === undefined) return fallback;
  if (typeof value !== "string" || value.length > 512) throw new Error("plugin_catalog_invalid");
  return value;
}

function stringList(value: unknown): string[] {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.length > MAX_LIST) throw new Error("plugin_catalog_invalid");
  return value.map((item) => {
    if (typeof item !== "string" || item.length === 0 || item.length > 128) throw new Error("plugin_catalog_invalid");
    return item;
  });
}

function entry(value: unknown, tier: PluginTier): PluginEntry {
  const raw = record(value);
  return {
    name: name(raw.name),
    version: text(raw.version, "unknown"),
    status: text(raw.status, "unknown"),
    reason: raw.reason === null || raw.reason === undefined ? null : text(raw.reason),
    commands: stringList(raw.commands),
    tools: stringList(raw.tools),
    binarySha256: raw.binary_sha256 === null || raw.binary_sha256 === undefined
      ? null
      : text(raw.binary_sha256),
    removable: tier === "required" ? false : raw.removable !== false,
    tier,
  };
}

/** Parse the Runtime plugin list; required plugins are locked. */
export function parsePluginCatalog(value: unknown): PluginCatalog {
  const raw = record(value);
  if (raw.schema !== PLUGIN_LIST_SCHEMA) throw new Error("plugin_catalog_invalid");
  if (!Array.isArray(raw.plugins) || raw.plugins.length > MAX_PLUGINS) throw new Error("plugin_catalog_invalid");
  const installed = raw.plugins.map((item) => entry(item, "installed"));
  const requiredRaw = raw.required === undefined ? [] : raw.required;
  if (!Array.isArray(requiredRaw) || requiredRaw.length > MAX_LIST) throw new Error("plugin_catalog_invalid");
  const required = requiredRaw.map((item) => entry(item, "required"));
  const names = new Set<string>();
  const plugins = [...required, ...installed].filter((plugin) => {
    if (names.has(plugin.name)) return false;
    names.add(plugin.name);
    return true;
  });
  return {
    schema: PLUGIN_LIST_SCHEMA,
    root: raw.root === undefined || raw.root === null ? null : text(raw.root),
    plugins,
  };
}

/** Computer-use and browser-use require an explicit capability consent. */
export function requiresPluginConsent(pluginName: string): boolean {
  return DANGEROUS.has(pluginName.trim().toLowerCase());
}

export function canRemovePlugin(plugin: PluginEntry): boolean {
  return plugin.tier !== "required" && plugin.removable;
}

export function pluginOperationError(code: string): string {
  if (code === "preview_no_runtime") return "Abra o app desktop para gerenciar plugins; a prévia não instala pacotes.";
  if (code === "plugin_consent_required") return "Confirme o consentimento antes de habilitar esta capacidade.";
  if (code === "plugin_required_locked") return "Plugins obrigatórios não podem ser removidos.";
  if (code === "plugin_catalog_unavailable") return "O catálogo de plugins do Runtime não está disponível.";
  return "A operação de plugin falhou: " + code;
}
