import { describe, expect, it } from "vitest";
import {
  AUTHORITATIVE_HOST_PROVIDERS,
  canonicalAuthoritativeHostProvider,
  isAuthoritativeHostProvider,
  parseProviderSessionBinding,
} from "./provider_binding";

describe("authoritative provider session bindings", () => {
  it("covers every installed-host contract name", () => {
    expect(AUTHORITATIVE_HOST_PROVIDERS).toEqual([
      "claude",
      "codex",
      "opencode",
      "grok",
      "vscode",
      "antigravity",
      "pi",
      "kiro",
    ]);
    for (const provider of AUTHORITATIVE_HOST_PROVIDERS) {
      expect(isAuthoritativeHostProvider(provider)).toBe(true);
      expect(parseProviderSessionBinding({
        schema: "simplicio.desktop-provider-session-binding/v1",
        bound: true,
        session_id: "runtime-session",
        provider,
        redacted: true,
      }).provider).toBe(provider);
    }
  });

  it("leaves unknown hosts unknown", () => {
    expect(isAuthoritativeHostProvider("unknown-host")).toBe(false);
    expect(() => parseProviderSessionBinding({
      schema: "simplicio.desktop-provider-session-binding/v1",
      bound: true,
      session_id: "runtime-session",
      provider: "unknown-host",
      redacted: true,
    })).toThrow("provider_session_binding_invalid");
  });

  it("normalizes the existing Claude Code host label to the canonical Claude key", () => {
    expect(canonicalAuthoritativeHostProvider("claude-code")).toBe("claude");
    expect(parseProviderSessionBinding({
      schema: "simplicio.desktop-provider-session-binding/v1",
      bound: true,
      session_id: "runtime-session",
      provider: "claude-code",
      redacted: true,
    }).provider).toBe("claude");
  });
});
