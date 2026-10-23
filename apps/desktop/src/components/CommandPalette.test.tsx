import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { CommandPaletteList } from "./CommandPalette";
import { buildCatalogArgs, catalogCliLine, filterCatalog, parseDesktopCatalog } from "../catalog_ui";

const catalog = parseDesktopCatalog({
  schema: "simplicio.desktop-catalog/v1",
  version: "3.10.0",
  digest_sha256: "sha256:abc",
  entries: [
    {
      id: "context",
      owning_plugin: "fast",
      tier: "kernel",
      cli_syntax: "simplicio context",
      mcp_tool_name: "simplicio_context",
      args_schema: { type: "object", properties: { task: { type: "string", description: "task" }, limit: { type: "integer" } }, required: ["task"] },
      description: "Bounded task context",
      effect_class: "read_only",
      capabilities_requiring_consent: [],
      availability: "installed",
      version: "v1",
      changelog_excerpt: "",
    },
    {
      id: "run",
      owning_plugin: "runtime",
      tier: "kernel",
      cli_syntax: "simplicio run",
      mcp_tool_name: "simplicio_run",
      args_schema: { type: "object" },
      description: "Governed task",
      effect_class: "effectful",
      capabilities_requiring_consent: ["write"],
      availability: "installed",
      version: "v1",
      changelog_excerpt: "",
    },
  ],
});

const noop = () => undefined;

describe("command palette", () => {
  it("renders every entry and the equivalent CLI", () => {
    const html = renderToStaticMarkup(
      <CommandPaletteList catalog={catalog} query="" selected="context" values={{ task: "x" }} consent={false} busy={false} onQuery={noop} onSelect={noop} onValue={noop} onConsent={noop} onRun={noop} />,
    );
    expect(html).toContain("context");
    expect(html).toContain("run");
    expect(html).toContain("simplicio context --task x --json");
  });

  it("builds only catalog-declared arguments and requires consent metadata", () => {
    const entry = catalog.entries[0];
    expect(buildCatalogArgs(entry, { task: "hello", extra: "no" })).toEqual(["context", "--task", "hello", "--json"]);
    expect(() => buildCatalogArgs(entry, {})).toThrow("catalog_field_required:task");
    expect(filterCatalog(catalog.entries, "governed").map((item) => item.id)).toEqual(["run"]);
    expect(catalogCliLine(catalog.entries[1])).toContain("simplicio run");
  });
});
