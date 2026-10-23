#!/usr/bin/env python3
"""Install and verify the managed OpenCode enforcement plugin (#450).

OpenCode V2 does not load a bare ``.js`` file from the ``plugins`` list: the
configured path must be a plugin directory, and the module must default-export
an object with ``id`` plus ``setup``. The previous managed shape (an npm name,
then a local ``.js`` file) therefore either 404'd or was rejected at load time,
which is why native ``write``/``edit``/``shell`` calls were never intercepted.

This module owns the public, host-verifiable shape:

* ``~/.simplicio/hooks/opencode-simplicio/`` is the managed plugin directory
  containing ``index.js`` (V2 ``setup`` hook plus V1 ``server`` fallback) and a
  ``package.json`` declaring ``"type": "module"``.
* ``~/.config/opencode/opencode.json`` declares that directory under
  ``plugins``; legacy npm and bare-file references are replaced, while every
  unrelated plugin, MCP server, prompt and setting is preserved byte-for-byte
  by key.

``verify`` proves the plugin resolves and that its ``execute.before`` hook
actually rejects native programming tools, so the exit code is meaningful
instead of a config round-trip. It never mutates the config.

Usage:
    python3 scripts/opencode_plugin.py install --json
    python3 scripts/opencode_plugin.py verify --json
    python3 scripts/opencode_plugin.py repair --json   # alias of install
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins" / "simplicio" / "opencode"
SCHEMA = "simplicio.opencode-install/v1"
VERIFY_SCHEMA = "simplicio.opencode-verify/v1"
PLUGIN_ID = "opencode-simplicio"
LEGACY_NPM = "opencode-simplicio"
LEGACY_FILE = "opencode-simplicio.js"
CONFIG_RELATIVE = Path(".config") / "opencode" / "opencode.json"
PLUGIN_RELATIVE = Path(".simplicio") / "hooks" / PLUGIN_ID
NATIVE_TOOLS = ("read", "write", "edit", "shell")
PASSTHROUGH_TOOLS = (
    "simplicio_edit",
    "simplicio_file",
    "third_party_tool",
    "mcp__github__issue",
)

_NODE_PROBE = r"""
const payload = JSON.parse(process.argv[1]);
const mod = await import(payload.url);
const plugin = mod.default;
const out = { id: null, setup: typeof plugin?.setup, hook: null, blocked: [], leaked: [], v1: [] };
if (!plugin || typeof plugin !== "object") {
  console.log(JSON.stringify({ ok: false, reason: "default_export_missing", ...out }));
  process.exit(0);
}
out.id = typeof plugin.id === "string" ? plugin.id : null;
let registered = null;
const ctx = { tool: { hook: async (name, callback) => { registered = { name, callback }; } } };
if (typeof plugin.setup === "function") {
  await plugin.setup(ctx);
}
if (registered) {
  out.hook = registered.name;
  for (const tool of payload.native) {
    try { await registered.callback({ tool }); } catch { out.blocked.push(tool); }
  }
  for (const tool of payload.passthrough) {
    try { await registered.callback({ tool }); } catch { out.leaked.push(tool); }
  }
}
if (typeof plugin.server === "function") {
  const hooks = await plugin.server();
  const v1 = hooks?.["tool.execute.before"];
  if (typeof v1 === "function") {
    for (const tool of payload.native) {
      try { await v1({ tool }); } catch { out.v1.push(tool); }
    }
  }
}
const ok =
  out.id === "simplicio" &&
  out.setup === "function" &&
  out.hook === "execute.before" &&
  payload.native.every((tool) => out.blocked.includes(tool)) &&
  out.leaked.length === 0 &&
  payload.native.every((tool) => out.v1.includes(tool));
console.log(JSON.stringify({ ok, ...out }));
"""


def _normalize(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".simplicio.tmp")
    temporary.write_bytes(data)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def _load_config(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "config_missing"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}, "config_malformed"
    if not isinstance(document, dict):
        return {}, "config_malformed"
    return document, None


def _strings(entries: Any) -> list[str]:
    if isinstance(entries, str):
        return [entries]
    if not isinstance(entries, list):
        return []
    values: list[str] = []
    for entry in entries:
        if isinstance(entry, str):
            values.append(entry)
        elif isinstance(entry, dict) and isinstance(entry.get("package"), str):
            values.append(entry["package"])
    return values


def _is_managed_reference(value: str) -> bool:
    """True for a reference this installer owns (legacy or current)."""

    normalized = _normalize(value)
    if normalized == LEGACY_NPM:
        return True
    name = normalized.rsplit("/", 1)[-1]
    if name == LEGACY_FILE:
        return True
    if name == PLUGIN_ID and normalized.endswith(f"/.simplicio/hooks/{PLUGIN_ID}"):
        return True
    return False


def _filter(entries: Any) -> tuple[list[Any], list[str]]:
    """Drop managed references from a plugin list, preserving everything else."""

    if entries is None:
        return [], []
    if isinstance(entries, str):
        return ([], [entries]) if _is_managed_reference(entries) else ([entries], [])
    if not isinstance(entries, list):
        return entries, []
    kept: list[Any] = []
    removed: list[str] = []
    for entry in entries:
        if isinstance(entry, str) and _is_managed_reference(entry):
            removed.append(entry)
        elif (
            isinstance(entry, dict)
            and isinstance(entry.get("package"), str)
            and _is_managed_reference(entry["package"])
        ):
            removed.append(entry["package"])
        else:
            kept.append(entry)
    return kept, removed


def _plugin_payload(source: Path) -> dict[str, bytes]:
    index = source / "index.js"
    manifest = source / "package.json"
    if not index.is_file() or not manifest.is_file():
        raise FileNotFoundError(f"managed plugin source is incomplete: {source}")
    return {"index.js": index.read_bytes(), "package.json": manifest.read_bytes()}


def install(
    *,
    home: Path | None = None,
    config_path: Path | None = None,
    source: Path = SOURCE,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Write the managed plugin directory and reconcile the OpenCode config."""

    resolved_home = (home or Path.home()).expanduser().resolve()
    config = (config_path or (resolved_home / CONFIG_RELATIVE)).expanduser()
    plugin_dir = resolved_home / PLUGIN_RELATIVE
    payload = _plugin_payload(source)
    document, error = _load_config(config)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "host": "opencode",
        "ok": False,
        "dry_run": dry_run,
        "config": str(config),
        "plugin": {
            "id": PLUGIN_ID,
            "path": str(plugin_dir),
            "entry": str(plugin_dir / "index.js"),
            "api": "opencode-v2",
        },
        "write_set": [],
        "removed": [],
        "backup": None,
        "reasons": [],
    }
    if error == "config_malformed":
        receipt["reasons"].append("config_malformed")
        return receipt

    original = config.read_bytes() if config.exists() else b""
    plugins = document.get("plugins")
    if plugins is not None and not isinstance(plugins, (list, str)):
        receipt["reasons"].append("plugins_not_a_list")
        return receipt
    kept, removed = _filter(plugins)
    legacy = document.get("plugin")
    legacy_kept, legacy_removed = _filter(legacy)
    removed.extend(legacy_removed)

    updated = dict(document)
    updated["plugins"] = [*kept, str(plugin_dir)]
    if "plugin" in updated:
        if legacy_kept:
            updated["plugin"] = legacy_kept
        else:
            updated.pop("plugin", None)

    encoded = (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    changed = encoded != original
    writes = [str(plugin_dir / name) for name in payload]
    if not dry_run:
        for name, data in payload.items():
            target = plugin_dir / name
            if not target.exists() or target.read_bytes() != data:
                _atomic_write(target, data)
        if changed:
            if config.exists():
                backup = config.with_name(config.name + ".simplicio.bak")
                shutil.copy2(config, backup)
                receipt["backup"] = str(backup)
            _atomic_write(config, encoded)
    receipt["changed"] = changed
    receipt["removed"] = [
        value
        for value in removed
        if _normalize(value) != _normalize(str(plugin_dir))
        and not _normalize(value).endswith(f"/.simplicio/hooks/{PLUGIN_ID}")
    ]
    receipt["write_set"] = writes + ([str(config)] if changed else [])
    receipt["verification"] = verify(home=resolved_home, config_path=config)
    receipt["ok"] = bool(receipt["verification"]["ok"])
    return receipt


def _probe_node(entry: Path, node: str) -> dict[str, Any]:
    payload = json.dumps(
        {
            "url": entry.resolve().as_uri(),
            "native": list(NATIVE_TOOLS),
            "passthrough": list(PASSTHROUGH_TOOLS),
        }
    )
    completed = subprocess.run(
        [node, "--input-type=module", "-e", _NODE_PROBE, payload],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or not lines:
        return {"ok": False, "reason": "node_probe_failed", "stderr": completed.stderr[-2000:]}
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"ok": False, "reason": "node_probe_invalid", "stdout": completed.stdout[-2000:]}


def _static_hook(entry: Path) -> bool:
    try:
        text = entry.read_text(encoding="utf-8")
    except OSError:
        return False
    return "execute.before" in text and "enforceNativeTool" in text


def _runtime_integrate(binary: str | None) -> dict[str, Any]:
    if not binary:
        return {"ran": False, "reason": "simplicio_not_on_path"}
    try:
        completed = subprocess.run(
            [binary, "integrate", "verify", "--host", "opencode", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ran": False, "reason": type(exc).__name__}
    payload: Any = None
    for line in reversed([line for line in completed.stdout.splitlines() if line.strip()]):
        try:
            payload = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    return {
        "ran": True,
        "exit_code": completed.returncode,
        "ok": bool(payload.get("ok")) if isinstance(payload, dict) else None,
        "payload": payload,
        "note": "runtime verify still checks the retired file/npm shape; the public gate above is authoritative",
    }


def verify(
    *,
    home: Path | None = None,
    config_path: Path | None = None,
    node: str | None = None,
    runtime_binary: str | None = None,
) -> dict[str, Any]:
    """Read-only gate: resolved plugin directory plus a live hook probe."""

    resolved_home = (home or Path.home()).expanduser().resolve()
    config = (config_path or (resolved_home / CONFIG_RELATIVE)).expanduser()
    expected_dir = (resolved_home / PLUGIN_RELATIVE).resolve()
    report: dict[str, Any] = {
        "schema": VERIFY_SCHEMA,
        "host": "opencode",
        "ok": False,
        "config": {"path": str(config), "exists": config.exists(), "plugins_key": "plugins", "declared": []},
        "plugin": {
            "id": PLUGIN_ID,
            "expected_path": str(expected_dir),
            "path": None,
            "entry": None,
            "resolved": False,
            "api": "opencode-v2",
            "sha256": None,
            "hook": {"name": "execute.before", "registered": False, "verified": "none", "blocked": [], "leaked": []},
        },
        "mcp": {},
        "runtime_integrate": {},
        "reasons": [],
    }
    document, error = _load_config(config)
    if error:
        report["reasons"].append(error)
        report["runtime_integrate"] = _runtime_integrate(runtime_binary or shutil.which("simplicio"))
        return report

    declarations = _strings(document.get("plugins")) + _strings(document.get("plugin"))
    report["config"]["declared"] = declarations
    if any(_normalize(value) == LEGACY_NPM for value in declarations):
        report["reasons"].append("legacy_npm_reference")
    if any(_normalize(value).endswith(LEGACY_FILE) for value in declarations):
        report["reasons"].append("legacy_file_reference")

    resolved: Path | None = None
    for value in declarations:
        candidate = Path(value.replace("~", str(resolved_home), 1)) if value.startswith("~") else Path(value)
        if not candidate.is_absolute():
            candidate = (config.parent / candidate).resolve()
        if candidate.is_dir() and (candidate / "index.js").is_file():
            resolved = candidate
            break
    if resolved is None:
        report["reasons"].append("plugin_not_declared_or_missing")
        report["runtime_integrate"] = _runtime_integrate(runtime_binary or shutil.which("simplicio"))
        return report

    entry = resolved / "index.js"
    data = entry.read_bytes()
    report["plugin"].update(
        {
            "path": str(resolved),
            "entry": str(entry),
            "resolved": True,
            "sha256": _digest(data),
        }
    )
    if not (resolved / "package.json").is_file():
        report["reasons"].append("package_manifest_missing")
    if not _static_hook(entry):
        report["reasons"].append("hook_not_registered")
    else:
        report["plugin"]["hook"]["registered"] = True
        report["plugin"]["hook"]["verified"] = "static"

    probe_node = node if node is not None else shutil.which("node")
    if probe_node:
        probe = _probe_node(entry, probe_node)
        report["plugin"]["hook"]["probe"] = probe
        report["plugin"]["hook"]["blocked"] = probe.get("blocked", [])
        report["plugin"]["hook"]["leaked"] = probe.get("leaked", [])
        report["plugin"]["id_export"] = probe.get("id")
        if probe.get("ok"):
            report["plugin"]["hook"]["verified"] = "dynamic"
        else:
            report["reasons"].append(str(probe.get("reason") or "hook_not_blocking"))
    else:
        report["reasons"].append("node_unavailable_for_hook_probe")

    managed = document.get("mcp")
    if isinstance(managed, dict) and isinstance(managed.get("simplicio"), dict):
        entry_mcp = managed["simplicio"]
        environment = entry_mcp.get("environment") if isinstance(entry_mcp.get("environment"), dict) else {}
        report["mcp"] = {
            "key": "simplicio",
            "present": True,
            "profile": environment.get("SIMPLICIO_MCP_PROFILE"),
            "runtime_mode": environment.get("SIMPLICIO_RUNTIME_MODE"),
            "server_count": len(managed),
        }
    else:
        report["mcp"] = {"key": "simplicio", "present": False, "server_count": 0}
        report["reasons"].append("managed_mcp_entry_missing")

    report["runtime_integrate"] = _runtime_integrate(runtime_binary or shutil.which("simplicio"))
    report["ok"] = not report["reasons"]
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install and verify the managed OpenCode enforcement plugin (#450).")
    parser.add_argument("action", choices=("install", "repair", "verify"))
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--config", type=Path)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--node")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.action in {"install", "repair"}:
        result = install(home=args.home, config_path=args.config, source=args.source, dry_run=args.dry_run)
    else:
        result = verify(home=args.home, config_path=args.config, node=args.node)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        verb = "installed" if args.action != "verify" else "verified"
        state = "ok" if result["ok"] else "failed"
        print(f"opencode plugin {verb}: {state}")
        for reason in result.get("reasons", []):
            print(f"  - {reason}")
        if result.get("plugin", {}).get("path"):
            print(f"  plugin: {result['plugin']['path']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
