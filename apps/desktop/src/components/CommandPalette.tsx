import { useEffect, useMemo, useState } from "react";
import {
  catalogCliLine,
  entryRequiresConsent,
  filterCatalog,
  type CatalogEntry,
  type CatalogValues,
  type DesktopCatalog,
} from "../catalog_ui";
import { loadDesktopCatalog, runDesktopCatalogEntry } from "../bridge";

export function CommandPaletteList({
  catalog,
  query,
  selected,
  values,
  consent,
  busy,
  error,
  result,
  onQuery,
  onSelect,
  onValue,
  onConsent,
  onRun,
}: {
  catalog: DesktopCatalog | null;
  query: string;
  selected: string | null;
  values: CatalogValues;
  consent: boolean;
  busy: boolean;
  error?: string | null;
  result?: string | null;
  onQuery: (value: string) => void;
  onSelect: (entry: CatalogEntry) => void;
  onValue: (name: string, value: string | number | boolean) => void;
  onConsent: (value: boolean) => void;
  onRun: () => void;
}) {
  const entries = useMemo(() => (catalog ? filterCatalog(catalog.entries, query) : []), [catalog, query]);
  const entry = catalog?.entries.find((item) => item.id === selected) ?? entries[0] ?? null;
  if (!catalog) {
    return (
      <section className="panel command-palette" data-testid="command-palette" aria-label="Paleta de comandos">
        <p role="status">{error ? "Catálogo do Runtime indisponível: " + error : "Consultando o catálogo do Runtime…"}</p>
      </section>
    );
  }
  return (
    <section className="panel command-palette" data-testid="command-palette" aria-label="Paleta de comandos">
      <div className="session-feed-heading">
        <div>
          <h2>Paleta de comandos</h2>
          <p>{catalog.entries.length} comandos do catálogo; o CLI equivalente aparece em cada entrada.</p>
        </div>
        <span className="neutral-badge">digest {catalog.digest ? catalog.digest.slice(0, 12) : "não assinado"}</span>
      </div>
      <label className="ref-search">
        <input
          aria-label="Buscar comando"
          type="search"
          value={query}
          maxLength={120}
          placeholder="Buscar comando, plugin ou descrição"
          onChange={(event) => onQuery(event.target.value)}
        />
      </label>
      <div className="command-palette-body">
        <ul className="command-palette-list" aria-label="Comandos">
          {entries.map((item) => (
            <li key={item.id}>
              <button type="button" aria-pressed={entry?.id === item.id} onClick={() => onSelect(item)}>
                <strong>{item.id}</strong>
                <span>{item.tier} · {item.owningPlugin}</span>
              </button>
            </li>
          ))}
        </ul>
        {entry && (
          <div className="command-palette-detail">
            <h3>{entry.id}</h3>
            <p>{entry.description}</p>
            <p><code>{catalogCliLine(entry, values)}</code></p>
            {entry.fields.map((field) => (
              <label key={field.name}>
                {field.name}{field.required ? " *" : ""}
                {field.type === "boolean" ? (
                  <input
                    type="checkbox"
                    checked={values[field.name] === true}
                    onChange={(event) => onValue(field.name, event.target.checked)}
                  />
                ) : (
                  <input
                    type={field.type === "number" ? "number" : "text"}
                    value={String(values[field.name] ?? "")}
                    onChange={(event) => onValue(field.name, event.target.value)}
                  />
                )}
                {field.description && <small>{field.description}</small>}
              </label>
            ))}
            {entryRequiresConsent(entry) && (
              <label>
                <input type="checkbox" checked={consent} onChange={(event) => onConsent(event.target.checked)} />
                Autorizo esta capacidade: {entry.capabilities.join(", ")}
              </label>
            )}
            <button className="button button-primary" type="button" disabled={busy} onClick={onRun}>
              Executar
            </button>
            {error && <p role="status">{error}</p>}
            {result && <pre aria-label="Resultado do comando">{result}</pre>}
          </div>
        )}
      </div>
    </section>
  );
}

export function CommandPalette() {
  const [catalog, setCatalog] = useState<DesktopCatalog | null>(null);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [values, setValues] = useState<CatalogValues>({});
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  useEffect(() => {
    loadDesktopCatalog()
      .then((next) => setCatalog(next))
      .catch((failure) => {
        const code = failure instanceof Error ? failure.message : String(failure);
        if (code !== "preview_no_runtime") setError(code);
      });
  }, []);

  async function run() {
    if (!catalog) return;
    const entry = catalog.entries.find((item) => item.id === selected) ?? filterCatalog(catalog.entries, query)[0];
    if (!entry) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const value = await runDesktopCatalogEntry(entry.id, values, consent);
      setResult(JSON.stringify(value, null, 2).slice(0, 20_000));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    } finally {
      setBusy(false);
    }
  }

  return (
    <CommandPaletteList
      catalog={catalog}
      query={query}
      selected={selected}
      values={values}
      consent={consent}
      busy={busy}
      error={error}
      result={result}
      onQuery={setQuery}
      onSelect={(entry) => { setSelected(entry.id); setValues({}); setConsent(false); setResult(null); }}
      onValue={(name, value) => setValues((current) => ({ ...current, [name]: value }))}
      onConsent={setConsent}
      onRun={() => void run()}
    />
  );
}
