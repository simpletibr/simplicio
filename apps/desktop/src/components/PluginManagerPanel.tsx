import { useEffect, useState } from "react";
import {
  canRemovePlugin,
  pluginOperationError,
  requiresPluginConsent,
  type PluginCatalog,
  type PluginEntry,
} from "../plugin_manager";
import {
  installDesktopPlugin,
  loadDesktopPlugins,
  removeDesktopPlugin,
  updateDesktopPlugin,
} from "../bridge";

function PluginCard({
  plugin,
  busy,
  consentPending,
  onInstall,
  onRemove,
  onUpdate,
  onConsent,
}: {
  plugin: PluginEntry;
  busy: boolean;
  consentPending: boolean;
  onInstall: (plugin: PluginEntry, consent: boolean) => void;
  onRemove: (plugin: PluginEntry) => void;
  onUpdate: (plugin: PluginEntry) => void;
  onConsent: (plugin: PluginEntry) => void;
}) {
  const dangerous = requiresPluginConsent(plugin.name);
  return (
    <article className="ref-plugin-card" key={plugin.name}>
      <div className="ref-plugin-title">
        <span className="ref-monogram">{plugin.name.slice(0, 2).toUpperCase()}</span>
        <div>
          <h3>{plugin.name}</h3>
          <span>versão {plugin.version}</span>
        </div>
      </div>
      <p>{plugin.commands.length > 0 ? "Comandos: " + plugin.commands.join(", ") : "Pacote sem comandos publicados."}</p>
      <div className="ref-plugin-tags">
        <span className="neutral-badge">{plugin.tier === "required" ? "obrigatório" : "opcional"}</span>
        <span className="neutral-badge">{plugin.status}</span>
        {dangerous && <span className="neutral-badge">consentimento necessário</span>}
      </div>
      {plugin.reason && <p role="status">{plugin.reason}</p>}
      <div className="ref-action-row">
        {consentPending ? (
          <button className="button button-primary" type="button" disabled={busy} onClick={() => onInstall(plugin, true)}>
            Permitir e instalar
          </button>
        ) : (
          <button className="button button-primary" type="button" disabled={busy} onClick={() => (dangerous ? onConsent(plugin) : onInstall(plugin, false))}>
            {plugin.tier === "required" ? "Reinstalar" : "Instalar"}
          </button>
        )}
        <button className="button button-secondary" type="button" disabled={busy} onClick={() => onUpdate(plugin)}>
          Atualizar
        </button>
        <button className="button button-secondary" type="button" disabled={busy || !canRemovePlugin(plugin)} onClick={() => onRemove(plugin)}>
          Remover
        </button>
      </div>
      {plugin.tier === "required" && <p>Plugin obrigatório: não pode ser removido.</p>}
    </article>
  );
}

export function PluginManagerList({
  catalog,
  busy = false,
  error,
  consentPending = null,
  onInstall,
  onRemove,
  onUpdate,
  onConsent,
}: {
  catalog: PluginCatalog | null;
  busy?: boolean;
  error?: string | null;
  consentPending?: string | null;
  onInstall: (plugin: PluginEntry, consent: boolean) => void;
  onRemove: (plugin: PluginEntry) => void;
  onUpdate: (plugin: PluginEntry) => void;
  onConsent: (plugin: PluginEntry) => void;
}) {
  if (!catalog) {
    return (
      <section className="ref-plugin-manager" aria-label="Plugins desta máquina" data-testid="plugin-manager">
        <p role="status">{error ? pluginOperationError(error) : "Consultando plugins do Runtime…"}</p>
      </section>
    );
  }
  return (
    <section className="ref-plugin-manager" aria-label="Plugins desta máquina" data-testid="plugin-manager">
      <div className="ref-plugin-toolbar">
        <div>
          <h2>Plugins desta máquina</h2>
          <p>Inventário do Runtime; obrigatórios ficam bloqueados e capacidades perigosas exigem consentimento.</p>
        </div>
        <span className="neutral-badge">{catalog.plugins.length} plugin(s)</span>
      </div>
      {error && <p role="status">{pluginOperationError(error)}</p>}
      <div className="ref-plugin-grid">
        {catalog.plugins.map((plugin) => (
          <PluginCard
            key={plugin.name}
            plugin={plugin}
            busy={busy}
            consentPending={consentPending === plugin.name}
            onInstall={onInstall}
            onRemove={onRemove}
            onUpdate={onUpdate}
            onConsent={onConsent}
          />
        ))}
      </div>
    </section>
  );
}

export function PluginManagerPanel() {
  const [catalog, setCatalog] = useState<PluginCatalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [consentPending, setConsentPending] = useState<string | null>(null);

  async function refresh() {
    try {
      setCatalog(await loadDesktopPlugins());
      setError(null);
    } catch (failure) {
      const code = failure instanceof Error ? failure.message : String(failure);
      setError(code === "preview_no_runtime" ? null : code);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function mutate(action: () => Promise<unknown>) {
    setBusy(true);
    setError(null);
    try {
      await action();
      setConsentPending(null);
      await refresh();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    } finally {
      setBusy(false);
    }
  }

  return (
    <PluginManagerList
      catalog={catalog}
      busy={busy}
      error={error}
      consentPending={consentPending}
      onInstall={(plugin, consent) => void mutate(() => installDesktopPlugin(plugin.name, consent))}
      onRemove={(plugin) => void mutate(() => removeDesktopPlugin(plugin.name))}
      onUpdate={(plugin) => void mutate(() => updateDesktopPlugin(plugin.name))}
      onConsent={(plugin) => setConsentPending(plugin.name)}
    />
  );
}
