import type { CostProjection, CostRow, CostTotals } from "./cost_projection";

export interface RoiDigest {
  markdown: string;
  measuredRows: number;
  estimatedRows: number;
  unknownRows: number;
}

const WINDOW_SECONDS = 7 * 24 * 60 * 60;

export function weeklyWindow(nowEpochSeconds: number): { from_epoch: number; to_epoch: number } {
  if (!Number.isSafeInteger(nowEpochSeconds) || nowEpochSeconds <= WINDOW_SECONDS) {
    throw new Error("roi_window_invalid");
  }
  return { from_epoch: nowEpochSeconds - WINDOW_SECONDS, to_epoch: nowEpochSeconds };
}

function number(value: number | null): string {
  return value === null ? "—" : value.toLocaleString("pt-BR");
}

function money(value: number | null): string {
  return value === null ? "—" : "US$ " + value.toFixed(6);
}

function totalsLine(label: string, totals: CostTotals): string {
  return [
    "| " + label + " | " + number(totals.event_count) + " | " + number(totals.actual_tokens),
    number(totals.baseline_tokens), number(totals.saved_tokens), money(totals.actual_cost_usd),
    money(totals.baseline_cost_usd), money(totals.saved_cost_usd) + " |",
  ].join(" | ");
}

function rowLine(row: CostRow): string {
  return "| " + [row.provider, row.model, row.host, row.project_id, row.execution, row.state,
    row.confidence, number(row.actual_tokens), money(row.actual_cost_usd), row.reason ?? ""].join(" | ") + " |";
}

/**
 * Build a weekly digest from the Runtime cost projection. Estimated or
 * unavailable rows are kept in their own section and are never counted as
 * measured; unknown values stay "—", never zero.
 */
export function buildRoiDigest(projection: CostProjection, window: { from_epoch: number; to_epoch: number }): RoiDigest {
  const measured = projection.rows.filter((row) => row.state === "measured" || row.state === "provider-reported");
  const estimated = projection.rows.filter((row) => row.state === "estimated");
  const unknown = projection.rows.filter((row) => row.state === "unavailable");
  const lines = [
    "# Digest semanal Simplicio",
    "",
    "Período: " + new Date(window.from_epoch * 1000).toISOString() + " → " + new Date(window.to_epoch * 1000).toISOString(),
    "Runtime revision: " + projection.usage_revision,
    "Report digest: " + projection.metadata.report_digest,
    "Cobertura: " + projection.metadata.coverage.status,
    "Pricing: " + projection.pricing.status + " (" + (projection.pricing.identity ?? "identidade não informada") + ")",
    "",
    "## Totais",
    "",
    "| grupo | eventos | tokens reais | baseline | economia | custo real | custo baseline | custo economizado |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
    totalsLine("total", projection.totals),
    "",
    "## Medido / provider-reported",
    "",
    measured.length === 0 ? "Nenhuma linha medida." : "| provider | modelo | host | projeto | execução | estado | confiança | tokens | custo | motivo |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + measured.map(rowLine).join("\n"),
    "",
    "## Estimado (não é medição)",
    "",
    estimated.length === 0 ? "Nenhuma linha estimada." : "| provider | modelo | host | projeto | execução | estado | confiança | tokens | custo | motivo |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + estimated.map(rowLine).join("\n"),
    "",
    "## Indisponível",
    "",
    unknown.length === 0 ? "Nenhuma linha indisponível." : unknown.map((row) => "- " + row.provider + "/" + row.model + ": " + (row.reason ?? "sem motivo informado")).join("\n"),
    "",
    "Valores estimados permanecem separados e rotulados. Campos sem evidência aparecem como —.",
    "",
  ];
  return {
    markdown: lines.join("\n"),
    measuredRows: measured.length,
    estimatedRows: estimated.length,
    unknownRows: unknown.length,
  };
}

export function downloadRoiDigest(digest: RoiDigest, filename = "simplicio-digest-semanal.md"): void {
  if (typeof document === "undefined" || typeof URL === "undefined") throw new Error("roi_download_unavailable");
  const blob = new Blob([digest.markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
