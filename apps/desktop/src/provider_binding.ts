export const AUTHORITATIVE_HOST_PROVIDERS = [
  "claude",
  "codex",
  "opencode",
  "grok",
  "vscode",
  "antigravity",
  "pi",
  "kiro",
] as const;

export type AuthoritativeHostProvider = typeof AUTHORITATIVE_HOST_PROVIDERS[number];
export type DesktopHostProvider = AuthoritativeHostProvider | "claude-code";

export const PROVIDER_SESSION_BINDING_SCHEMA =
  "simplicio.desktop-provider-session-binding/v1";

export type ProviderSessionBinding = {
  schema: typeof PROVIDER_SESSION_BINDING_SCHEMA;
  bound: true;
  sessionId: string;
  provider: AuthoritativeHostProvider;
  redacted: true;
};

export function isAuthoritativeHostProvider(
  provider: string,
): provider is AuthoritativeHostProvider {
  return canonicalAuthoritativeHostProvider(provider) !== null;
}

export function canonicalAuthoritativeHostProvider(
  provider: string,
): AuthoritativeHostProvider | null {
  if (provider === "claude-code") return "claude";
  return (AUTHORITATIVE_HOST_PROVIDERS as readonly string[]).includes(provider)
    ? provider as AuthoritativeHostProvider
    : null;
}

export function parseProviderSessionBinding(value: unknown): ProviderSessionBinding {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("provider_session_binding_invalid");
  }
  const raw = value as Record<string, unknown>;
  const provider = typeof raw.provider === "string"
    ? canonicalAuthoritativeHostProvider(raw.provider)
    : null;
  if (
    raw.schema !== PROVIDER_SESSION_BINDING_SCHEMA
    || raw.bound !== true
    || typeof raw.session_id !== "string"
    || raw.session_id.length === 0
    || raw.session_id.length > 512
    || provider === null
    || raw.redacted !== true
  ) {
    throw new Error("provider_session_binding_invalid");
  }
  return {
    schema: PROVIDER_SESSION_BINDING_SCHEMA,
    bound: true,
    sessionId: raw.session_id,
    provider,
    redacted: true,
  };
}
