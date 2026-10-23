import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { PluginManagerList } from "./PluginManagerPanel";
import { parsePluginCatalog } from "../plugin_manager";

const catalog = parsePluginCatalog({
  schema: "simplicio.plugin-list/v1",
  root: "/home/u/.simplicio",
  required: [{ name: "simplicio-loop", version: "0.1.0", bundled: true, removable: false, commands: ["loop"], tools: [] }],
  plugins: [
    { name: "simplicio-browser-use", version: "0.1.0", status: "ok", reason: null, commands: ["browser-use"], tools: ["plugin_browser_use"], binary_sha256: "sha256:abc" },
  ],
});

const noop = () => undefined;

describe("PluginManagerList", () => {
  it("locks required plugins and asks for consent before dangerous capabilities", () => {
    const html = renderToStaticMarkup(
      <PluginManagerList catalog={catalog} consentPending="simplicio-browser-use" onInstall={noop} onRemove={noop} onUpdate={noop} onConsent={noop} />,
    );
    expect(html).toContain("simplicio-loop");
    expect(html).toContain("obrigatório");
    expect(html).toContain("Plugin obrigatório: não pode ser removido.");
    expect(html).toContain("consentimento necessário");
    expect(html).toContain("Permitir e instalar");
    expect(html).toContain("simplicio-browser-use");
  });

  it("shows a Runtime error without inventing an inventory", () => {
    const html = renderToStaticMarkup(
      <PluginManagerList catalog={null} error="plugin_catalog_unavailable" onInstall={noop} onRemove={noop} onUpdate={noop} onConsent={noop} />,
    );
    expect(html).toContain("catálogo de plugins do Runtime");
    expect(html).not.toContain("Remover");
  });
});
