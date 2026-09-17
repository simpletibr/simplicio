# macOS arm64 installed-acceptance gate

This Linux workspace cannot close issue #375. The remaining gate is installed
evidence on Wesley's Mac (macOS arm64). Do not invent a `.sig`, do not fabricate
a notarized install report, and do not overwrite the user's only working
install.

## Blocked here

- Matching Desktop DMG signature: the published `Simplicio-3.8.47-arm64.dmg` has
  no companion `Simplicio-3.8.47-arm64.dmg.sig`. The Runtime sidecar `.sig` is
  not a Desktop installer signature.
- Signed/notarized download, install, relaunch, startup health, and rollback on
  a separate test copy. Apple Developer ID and notarization cannot be inferred
  from an ad-hoc or Linux build.
- Native logout/relogin and the permission grant/deny matrix in the installed
  WebView, without bypassing human authentication.
- Live installed Codex/Grok quota matrix and live host-plugin catalog update
  effects against the actual catalog on that Mac.

## What a Mac owner must attach

Follow `docs/desktop/INSTALLED-E2E.md`. Use a separate test install and an
isolated clean HOME. Write one redacted report under
`reports/desktop-installed/macos-arm64-<run>.json` and run:

```bash
python3 scripts/verify_desktop_installed_acceptance.py \
  --evidence reports/desktop-installed/macos-arm64-<run>.json --json
```

The report is `READY` only when every required check is `verified`, including
`host_plugin_freshness`. Blocked or unexecuted checks keep #375 open.
