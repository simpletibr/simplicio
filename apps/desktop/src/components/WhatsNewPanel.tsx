import { useEffect, useState } from "react";
import type { DesktopCatalog } from "../catalog_ui";
import { loadDesktopCatalog } from "../bridge";

export function WhatsNewList({ catalog }: { catalog: DesktopCatalog | null }) {
  if (!catalog) {
    return (
      <section className="panel whats-new" data-testid="whats-new" aria-label="Novidades">
        <p role="status">Consultando novidades do catálogo do Runtime…</p>
      </section>
    );
  }
  const entries = catalog.entries.filter((entry) => entry.changelogExcerpt.trim().length > 0).slice(0, 20);
  return (
    <section className="panel whats-new" data-testid="whats-new" aria-label="Novidades">
      <div className="session-feed-heading">
        <div>
          <h2>Novidades do catálogo</h2>
          <p>Comandos e plugins anunciados pelo Runtime {catalog.version}; nada aqui exige uma nova versão do Desktop.</p>
        </div>
        <span className="neutral-badge">{entries.length} item(ns)</span>
      </div>
      {entries.length === 0 ? <p role="status">Nenhum changelog publicado neste catálogo.</p> : (
        <ul>
          {entries.map((entry) => (
            <li key={entry.id}>
              <strong>{entry.id}</strong> <span>({entry.tier} · {entry.owningPlugin})</span>
              <p>{entry.changelogExcerpt}</p>
              <code>{entry.cliSyntax}</code>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function WhatsNewPanel() {
  const [catalog, setCatalog] = useState<DesktopCatalog | null>(null);
  useEffect(() => {
    loadDesktopCatalog()
      .then((next) => setCatalog(next))
      .catch(() => setCatalog({ schema: "simplicio.desktop-catalog/v1", version: "unknown", digest: null, entries: [] }));
  }, []);
  return <WhatsNewList catalog={catalog} />;
}
