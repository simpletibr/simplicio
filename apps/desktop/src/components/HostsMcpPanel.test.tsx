import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { HostsMcpList } from "./HostsMcpPanel";
import { parseHostsPlan } from "../hosts_plan";

const plan = parseHostsPlan({
  schema: "simplicio.mcp-register-plan/v1",
  status: "planned",
  binary: "C:/Users/u/.simplicio/bin/simplicio.exe",
  writes: [
    { label: "claude-code", kind: "replace", path: "C:/Users/u/.claude.json", current: "{\"SIMPLICIO_MCP_PROFILE\": \"mapper-only\"}" },
    { label: "cursor", kind: "noop", path: "C:/Users/u/.cursor/mcp.json", current: "{}" },
  ],
});

describe("HostsMcpList", () => {
  it("renders detected hosts and mapper-only compliance", () => {
    const html = renderToStaticMarkup(<HostsMcpList plan={plan} busy={false} onRepair={() => undefined} />);
    expect(html).toContain("claude-code");
    expect(html).toContain("cursor");
    expect(html).toContain("já registrado");
    expect(html).toContain("Reparar registros");
  });

  it("does not invent a host list when the plan is unavailable", () => {
    const html = renderToStaticMarkup(<HostsMcpList plan={null} busy={false} error="hosts_plan_unavailable" onRepair={() => undefined} />);
    expect(html).toContain("Plano de hosts indisponível");
    expect(html).not.toContain("<tbody>");
  });
});
