import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { WhatsNewList } from "./WhatsNewPanel";
import { parseDesktopCatalog } from "../catalog_ui";

const catalog = parseDesktopCatalog({
  schema: "simplicio.desktop-catalog/v1",
  version: "3.10.0",
  digest_sha256: null,
  entries: [
    { id: "context", owning_plugin: "fast", tier: "kernel", cli_syntax: "simplicio context", mcp_tool_name: "simplicio_context", args_schema: { type: "object" }, description: "ctx", effect_class: "read_only", capabilities_requiring_consent: [], availability: "installed", version: "v1", changelog_excerpt: "Fast context is now incremental." },
    { id: "version", owning_plugin: "runtime", tier: "kernel", cli_syntax: "simplicio version", mcp_tool_name: null, args_schema: { type: "object" }, description: "v", effect_class: "read_only", capabilities_requiring_consent: [], availability: "installed", version: "1", changelog_excerpt: "" },
  ],
});

describe("WhatsNewList", () => {
  it("lists catalog changelog entries with tier and CLI", () => {
    const html = renderToStaticMarkup(<WhatsNewList catalog={catalog} />);
    expect(html).toContain("Fast context is now incremental.");
    expect(html).toContain("simplicio context");
    expect(html).not.toContain("simplicio version");
  });
});
