import { useEffect, useState } from "react";
import type { CostProjection } from "../cost_projection";
import { loadDesktopCostProjection } from "../bridge";
import { buildRoiDigest, downloadRoiDigest, weeklyWindow, type RoiDigest } from "../roi_digest";

export function RoiDigestCard({ digest, error }: { digest: RoiDigest | null; error?: string | null }) {
  if (!digest) {
    return (
      <section className="panel roi-digest" data-testid="roi-digest" aria-label="Digest semanal">
        <p role="status">{error ? "Digest indisponível: " + error : "Gerando digest semanal a partir do Runtime…"}</p>
      </section>
    );
  }
  return (
    <section className="panel roi-digest" data-testid="roi-digest" aria-label="Digest semanal">
      <div className="session-feed-heading">
        <div>
          <h2>Digest semanal</h2>
          <p>{digest.measuredRows} linha(s) medida(s), {digest.estimatedRows} estimada(s), {digest.unknownRows} indisponível(is).</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => downloadRoiDigest(digest)}>
          Baixar Markdown
        </button>
      </div>
      <pre aria-label="Markdown do digest semanal">{digest.markdown}</pre>
    </section>
  );
}

export function RoiDigestPanel({ repoPath }: { repoPath?: string }) {
  const [digest, setDigest] = useState<RoiDigest | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const now = Math.floor(Date.now() / 1000);
    const window = weeklyWindow(now);
    loadDesktopCostProjection(window, repoPath)
      .then((projection: CostProjection) => {
        if (active) setDigest(buildRoiDigest(projection, window));
      })
      .catch((failure: unknown) => {
        if (!active) return;
        const code = failure instanceof Error ? failure.message : String(failure);
        if (code !== "preview_no_runtime") setError(code);
      });
    return () => { active = false; };
  }, [repoPath]);

  return <RoiDigestCard digest={digest} error={error} />;
}
