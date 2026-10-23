import { expect, test, type Page } from "@playwright/test";
import { createDemoSnapshot } from "../src/demo";
import type { DesktopSnapshot } from "../src/contracts";

/**
 * Responsive proof for #468: at 375 px and 480 px the read-mostly fleet layout
 * must not scroll horizontally, and the steering controls must exist only for
 * the online machine that accepted the token.
 */
function runtimeSnapshot(): DesktopSnapshot {
  const snapshot = structuredClone(createDemoSnapshot("active"));
  snapshot.source = "runtime";
  if (snapshot.botCenter) snapshot.botCenter.source = "runtime";
  return snapshot;
}

const fleet = {
  schema: "simplicio.desktop-remote-fleet/v1",
  configured: true,
  redacted: true,
  observedAt: 1_900_000_000,
  error: null,
  remotes: [
    {
      id: "mac-mini",
      label: "Mac mini",
      url: "http://127.0.0.1:8787/a/very/long/base/path/that/must/wrap/instead/of/scrolling",
      status: "online",
      authenticated: true,
      version: "3.10.0",
      latencyMs: 18,
      reasonCode: null,
      workers: [
        {
          id: "w-1",
          label: "issue-468-mobile-steer",
          claim: "issue:468",
          state: "running",
          progress: { done: 3, total: 7 },
          receiptId: "rcpt-468-abc",
        },
        {
          id: "w-2",
          label: "review-fleet",
          claim: "branch:feat/fleet-review",
          state: "paused",
          progress: null,
          receiptId: null,
        },
      ],
    },
    {
      id: "studio",
      label: "Studio",
      url: "https://studio.example.test",
      status: "offline",
      authenticated: false,
      version: null,
      latencyMs: null,
      reasonCode: "remote_unreachable",
      workers: [
        {
          id: "w-9",
          label: "blocked-worker",
          claim: "issue:470",
          state: "blocked",
          progress: { done: 0, total: null },
          receiptId: null,
        },
      ],
    },
  ],
};

async function mockRuntime(page: Page) {
  await page.addInitScript(
    ({ snapshot, fleet }) => {
      let callbackId = 0;
      Object.assign(window, {
        isTauri: true,
        __TAURI_EVENT_PLUGIN_INTERNALS__: { unregisterListener: () => undefined },
        __TAURI_INTERNALS__: {
          transformCallback: () => ++callbackId,
          invoke: async (command: string) => {
            if (command === "plugin:event|listen") return ++callbackId;
            if (command === "plugin:event|unlisten") return undefined;
            if (command === "desktop_runtime_install_status") {
              return { schema: "simplicio.desktop-install-status/v1", status: "clear", redacted: true };
            }
            if (command === "desktop_preparation_status") return true;
            if (command === "desktop_snapshot" || command === "refresh_desktop_snapshot") return snapshot;
            if (command === "desktop_remote_fleet") return fleet;
            // Any other screen keeps its empty state; this spec is about layout.
            return null;
          },
        },
      });
    },
    { snapshot: runtimeSnapshot(), fleet },
  );
}

for (const width of [375, 480] as const) {
  test(`mobile fleet stays inside ${width}px without horizontal scroll`, async ({ page }, testInfo) => {
    await page.setViewportSize({ width, height: 740 });
    await mockRuntime(page);
    await page.goto("/?view=quick-commands");

    const panel = page.locator('[data-testid="mobile-fleet"]');
    await expect(panel).toBeVisible();
    await expect(panel).toHaveAttribute("data-width", String(width));
    await expect(panel).toContainText("Mac mini");
    await expect(panel).toContainText("issue:468");
    await expect(panel).toContainText("3/7 passo(s)");
    await expect(panel).toContainText("rcpt-468-abc");

    // The documented proof: nothing overflows the window or the panel.
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    expect(await page.evaluate(() => document.body.scrollWidth <= window.innerWidth)).toBe(true);
    expect(await panel.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);

    // Steering controls: pause/resume only, only for the authorized machine.
    const pause = panel.locator('[data-testid="mobile-steer-mac-mini-w-1-pause"]');
    const resumeRunning = panel.locator('[data-testid="mobile-steer-mac-mini-w-1-resume"]');
    await expect(pause).toBeEnabled();
    await expect(resumeRunning).toBeDisabled();
    await expect(resumeRunning).toHaveAttribute("aria-describedby", "mobile-steer-hint-mac-mini-w-1-resume");
    await expect(panel.locator('[data-testid="mobile-steer-mac-mini-w-2-resume"]')).toBeEnabled();
    await expect(panel.locator('[data-testid="mobile-steer-mac-mini-w-2-pause"]')).toBeDisabled();
    expect(await panel.evaluate((element) => element.querySelectorAll('[data-testid^="mobile-steer-studio"]').length)).toBe(0);
    await expect(panel).toContainText("A máquina está offline");

    await panel.screenshot({ path: testInfo.outputPath(`mobile-fleet-${width}.png`) });
  });
}
