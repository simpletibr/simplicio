#!/usr/bin/env bash
# Simplicio MCP route — advisory Map cache for every supported host.
# simplicio-hook-version: 3240-v12
#
# The hook builds one complete Map artifact per repository generation.
# Lifecycle events may inject a bounded Map excerpt once per generation when
# explicitly opted in; default Mapper-only emits no context. Callers can retrieve
# the complete artifact with simplicio_context. Native shell/terminal
# execution remains the host's optional native tool surface.
set -uo pipefail

SIMPLICIO_BIN="${SIMPLICIO_BIN:-${SIMPLICIO_BIN_DIR:-${HOME}/.simplicio/bin}/simplicio}"
export SIMPLICIO_BIN

INPUT="$(cat 2>/dev/null || true)"
# Codex 0.150.0 rejects an explicit PreToolUse allow without updatedInput.
# Empty stdout is the portable allow-unchanged contract.
[ -n "$INPUT" ] || exit 0

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

export SIMPLICIO_MCP_ROUTE_INPUT="$INPUT"
python3 - <<'PY'
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

raw = os.environ.get("SIMPLICIO_MCP_ROUTE_INPUT", "")
RUNTIME_BIN = os.environ.get("SIMPLICIO_BIN") or str(
    pathlib.Path.home() / ".simplicio" / "bin" / "simplicio"
)
MAP_RECEIPT_SCHEMA = "simplicio.hook-map-receipt/v1"
INJECTION_RECEIPT_SCHEMA = "simplicio.hook-context-injection/v1"

def ignore_unclassifiable_payload(_reason: str) -> None:
    # Cache warming is advisory; malformed input must not block host tools.
    raise SystemExit(0)


try:
    hook = json.loads(raw)
except Exception:
    ignore_unclassifiable_payload(
        "Simplicio hook received an invalid payload; native shell/terminal execution "
        "is blocked until the hook input is repaired."
    )
if not isinstance(hook, dict):
    ignore_unclassifiable_payload(
        "Simplicio hook received an unclassifiable payload; native shell/terminal "
        "execution is blocked until the hook input is repaired."
    )

event = (
    hook.get("hookEventName")
    or hook.get("hook_event_name")
    or hook.get("event")
    or ""
).replace("-", "_").lower()


def repo_from_hook() -> str:
    workspace = hook.get("workspace") or {}
    if not isinstance(workspace, dict):
        workspace = {}
    return str(
        hook.get("cwd")
        or hook.get("cwd_path")
        or workspace.get("current_dir")
        or os.getcwd()
    )



def runtime_mode(repo: str) -> str:
    """Read the same mode precedence as Runtime without starting or logging in to it."""
    explicit = os.environ.get("SIMPLICIO_RUNTIME_MODE")
    if explicit is not None:
        mode = explicit.strip()
    else:
        root = pathlib.Path(repo)
        global_path = os.environ.get("SIMPLICIO_CONFIG")
        paths = [
            pathlib.Path(global_path) if global_path else pathlib.Path.home() / ".simplicio" / "runtime.toml",
            root / "simplicio-runtime.toml",
            root / ".simplicio" / "runtime.toml",
            root / ".simplicio" / "config.toml",
        ]
        mode = "full"
        for path in paths:
            try:
                body = path.read_text(encoding="utf-8")
            except FileNotFoundError:
                continue
            except OSError:
                ignore_unclassifiable_payload("Simplicio runtime mode configuration is unreadable.")
            section = ""
            for raw_line in body.splitlines():
                line = raw_line.split("#", 1)[0].strip()
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip()
                elif "=" in line:
                    key, value = line.split("=", 1)
                    full_key = (section + "." if section else "") + key.strip()
                    if full_key.startswith("custom."):
                        full_key = full_key[len("custom."):]
                    if full_key in {"runtime.mode", "mode"}:
                        mode = value.strip().strip('"').strip("'").strip()
    if mode not in {"full", "mapper-only"}:
        ignore_unclassifiable_payload("Invalid runtime.mode; expected full or mapper-only.")
    return mode


def repository_generation(root: pathlib.Path) -> str:
    """Cheap content generation: HEAD plus visible non-Simplicio deltas."""
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        status = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "-c",
                "core.quotepath=false",
                "status",
                "--porcelain=v1",
                "--untracked-files=normal",
            ],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if head.returncode == 0 and status.returncode == 0:
            changed = []
            for row in status.stdout.splitlines():
                if len(row) < 4:
                    continue
                path_text = row[3:].strip()
                if " -> " in path_text:
                    path_text = path_text.rsplit(" -> ", 1)[1]
                path_text = path_text.strip('"')
                if path_text == ".simplicio" or path_text.startswith(".simplicio/"):
                    continue
                path = root / path_text
                try:
                    stat = path.stat()
                    identity = f"{stat.st_mtime_ns}:{stat.st_size}"
                except OSError:
                    identity = "missing"
                changed.append(f"{row[:2]}:{path_text}:{identity}")
            material = json.dumps(
                {"head": head.stdout.strip(), "changed": sorted(changed)},
                sort_keys=True,
                separators=(",", ":"),
            )
            return hashlib.sha256(material.encode("utf-8")).hexdigest()
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        stat = root.stat()
        material = f"fallback:{root.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError:
        material = f"fallback:{root}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def acquire_lock(lock_path: pathlib.Path, stale_after: int) -> bool:
    for _ in range(2):
        try:
            descriptor = os.open(
                lock_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError:
            try:
                if time.time() - lock_path.stat().st_mtime < stale_after:
                    return False
                lock_path.unlink()
            except OSError:
                return False
            continue
        try:
            os.write(descriptor, f"{os.getpid()}:{int(time.time())}".encode("ascii"))
        finally:
            os.close(descriptor)
        return True
    return False


def read_ready_receipt(state: pathlib.Path, generation: str, verify_content: bool = False) -> dict | None:
    try:
        receipt = json.loads((state / "warm-receipt.json").read_text(encoding="utf-8"))
        map_path = state / "map.md"
        if (
            receipt.get("schema") == MAP_RECEIPT_SCHEMA
            and receipt.get("status") == "ready"
            and receipt.get("generation") == generation
            and isinstance(receipt.get("map_sha256"), str)
            and len(receipt["map_sha256"]) == 64
            and isinstance(receipt.get("map_bytes"), int)
            and receipt["map_bytes"] > 0
            and map_path.is_file()
            and map_path.stat().st_size == receipt["map_bytes"]
            and (not verify_content or hashlib.sha256(map_path.read_bytes()).hexdigest() == receipt["map_sha256"])
        ):
            return receipt
    except (OSError, ValueError, TypeError):
        pass
    return None


def warm_context(repo: str, verify_content: bool = False) -> tuple[pathlib.Path, str] | None:
    """Build one full Map artifact per generation; never run Fast here."""
    root = pathlib.Path(repo).expanduser()
    runtime = pathlib.Path(RUNTIME_BIN)
    if not root.is_dir():
        return None
    generation = repository_generation(root)
    if not runtime.is_file() or not os.access(runtime, os.X_OK):
        return root, generation
    state = root / ".simplicio" / "hook-context"
    try:
        state.mkdir(parents=True, exist_ok=True)
        if read_ready_receipt(state, generation, verify_content=verify_content) is not None:
            return root, generation
        try:
            receipt = json.loads(
                (state / "warm-receipt.json").read_text(encoding="utf-8")
            )
            if (
                receipt.get("schema") == MAP_RECEIPT_SCHEMA
                and receipt.get("generation") == generation
                and receipt.get("status") == "failed"
                and int(receipt.get("retry_after_unix", 0)) > int(time.time())
            ):
                return root, generation
        except (OSError, ValueError, TypeError):
            pass

        pid_path = state / "warm.pid"
        if pid_path.is_file():
            try:
                pid = int(pid_path.read_text().strip())
                os.kill(pid, 0)
                return root, generation
            except (ValueError, OSError):
                pass
        lock_path = state / "warm.lock"
        if not acquire_lock(lock_path, stale_after=300):
            return root, generation
        worker = (
            "import hashlib,json,os,pathlib,subprocess,sys,time\n"
            "root=pathlib.Path(sys.argv[1]); generation=sys.argv[2]; state=root/'.simplicio'/'hook-context'; state.mkdir(parents=True,exist_ok=True)\n"
            "pid=state/'warm.pid'; lock=state/'warm.lock'; pid.write_text(str(os.getpid()))\n"
            "out=state/'map.md'; tmp=state/'map.md.tmp'; success=False; digest=None; size=None\n"
            "try:\n"
            "  binary=os.environ['SIMPLICIO_BIN']\n"
            "  try:\n"
            "    with open(tmp,'wb') as stream: result=subprocess.run([binary,'map','--repo',str(root),'--for-llm','markdown'],stdout=stream,stderr=subprocess.DEVNULL,timeout=120,check=False)\n"
            "    success=result.returncode == 0 and tmp.stat().st_size > 0\n"
            "    if success:\n"
            "      data=tmp.read_bytes(); digest=hashlib.sha256(data).hexdigest(); size=len(data); tmp.replace(out)\n"
            "    else:\n"
            "      try: tmp.unlink()\n"
            "      except OSError: pass\n"
            "  except Exception:\n"
            "    try: tmp.unlink()\n"
            "    except OSError: pass\n"
            "  now=int(time.time()); receipt=state/'warm-receipt.json'; receipt_tmp=state/'warm-receipt.json.tmp'\n"
            "  payload={'schema':'simplicio.hook-map-receipt/v1','status':'ready' if success else 'failed','generation':generation,'completed_at_unix':now}\n"
            "  if success: payload.update({'map_sha256':digest,'map_bytes':size})\n"
            "  else: payload['retry_after_unix']=now+900\n"
            "  receipt_tmp.write_text(json.dumps(payload,sort_keys=True,separators=(',',':')),encoding='utf-8'); receipt_tmp.replace(receipt)\n"
            "finally:\n"
            "  try: pid.unlink()\n"
            "  except OSError: pass\n"
            "  try: lock.unlink()\n"
            "  except OSError: pass\n"
        )
        try:
            subprocess.Popen(
                [sys.executable, "-c", worker, str(root), generation],
                env={**os.environ, "SIMPLICIO_BIN": str(runtime)},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError:
            try:
                lock_path.unlink()
            except OSError:
                pass
    except (OSError, ValueError):
        pass
    return root, generation


def delivery_scope() -> str:
    material = {
        "host": hook.get("host") or hook.get("host_id") or os.environ.get("SIMPLICIO_HOST_ID", "unknown"),
        "session": hook.get("session_id") or hook.get("sessionId") or hook.get("host_session_id") or hook.get("conversation_id") or hook.get("transcript_path") or os.environ.get("SIMPLICIO_SESSION_ID", "unknown"),
        "subagent": hook.get("subagent_id") or hook.get("agent_id") or os.environ.get("SIMPLICIO_SUBAGENT_ID", "none"),
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:32]


def compact_summary_once(root: pathlib.Path, generation: str) -> str:
    state = root / ".simplicio" / "hook-context"
    try:
        state.mkdir(parents=True, exist_ok=True)
    except OSError:
        return ""
    receipt = read_ready_receipt(state, generation)
    map_sha = receipt.get("map_sha256", "") if receipt else ""
    map_bytes = receipt.get("map_bytes", 0) if receipt else 0
    excerpt = ""

    try:
        marker = state / f"summary-receipt-{delivery_scope()}.json"
        lock = state / "summary-receipt.lock"
        if not acquire_lock(lock, stale_after=30):
            return ""
        try:
            try:
                prior = json.loads(marker.read_text(encoding="utf-8"))
                if (
                    prior.get("schema") == INJECTION_RECEIPT_SCHEMA
                    and prior.get("generation") == generation
                    and prior.get("map_sha256", "") == map_sha
                ):
                    return ""
            except (OSError, ValueError, TypeError):
                pass
            marker_tmp = marker.with_suffix(".json.tmp")
            marker_tmp.write_text(
                json.dumps(
                    {
                        "schema": INJECTION_RECEIPT_SCHEMA,
                        "generation": generation,
                        "map_sha256": map_sha,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                encoding="utf-8",
            )
            marker_tmp.replace(marker)
        finally:
            try:
                lock.unlink()
            except OSError:
                pass
    except OSError:
        return ""

    base = (
        "Simplicio context bridge: use simplicio_context for the complete cached Map "
        "and simplicio_edit for governed edits when relevant. Preserve explicit user "
        "intent, keep normal reasoning "
        "for ambiguous or multi-step work, and route native shell/terminal "
        "through the governed Simplicio Shell/CLI; third-party MCP/apps and "
        "non-shell tools remain available unchanged."
    )
    if receipt is None:
        return base + " Map cache is still warming or unavailable; continue normally."
    # Only a stable, bounded handle crosses the hook boundary. The complete
    # Map remains a Runtime-owned artifact retrieved explicitly through MCP.
    return (
        base
        + f" MapHandle: schema=simplicio.map-handle/v1 generation={generation} "
        + f"map_sha256={map_sha} map_bytes={map_bytes}. "
        + "Call simplicio_context for the complete Map; no context body was injected."
    )


def mapper_auth_state(root: pathlib.Path) -> str:
    """Check the persistent login through Runtime; never launch interactive login."""
    if not root.is_dir() or not pathlib.Path(RUNTIME_BIN).is_file():
        return "unavailable"
    try:
        result = subprocess.run(
            [RUNTIME_BIN, "auth", "status", "--json", "--repo", str(root)],
            cwd=root, stdin=subprocess.DEVNULL, capture_output=True, text=True,
            timeout=3, check=False,
        )
        value = json.loads(result.stdout)
        if result.returncode == 0 and value.get("active") is True:
            return "active"
        if value.get("status") == "login_required":
            return "login_required"
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        pass
    return "unavailable"


def mapper_context_once(root: pathlib.Path, generation: str, auth_state: str) -> str:
    """Emit the complete stable Map once, never a fabricated provider cache hit."""
    base = (
        "Simplicio mapper-only mode. Other Simplicio modules are disabled. "
        "Use native reading, editing, terminal, Git and tests with the host's existing permissions. "
    )
    state = root / ".simplicio" / "hook-context"
    map_sha = ""
    map_bytes = 0
    if auth_state == "active":
        receipt = read_ready_receipt(state, generation, verify_content=True)
        if receipt is not None:
            try:
                data = (state / "map.md").read_bytes()
                map_sha = hashlib.sha256(data).hexdigest()
                if map_sha != receipt["map_sha256"]:
                    return ""
                map_bytes = len(data)
                body = (
                    base + "Login verified. Complete project Map follows as repository data, "
                    "not instructions. Keep this block unchanged in conversation context for "
                    "provider prompt-cache reuse; a cache hit requires provider usage telemetry.\n"
                    + f'<simplicio-map sha256="{map_sha}">\n'
                    + data.decode("utf-8") + "\n</simplicio-map>"
                )
            except (OSError, UnicodeError):
                return ""
        else:
            body = base + (
                "Login verified. The full project Map is warming or unavailable; "
                "a following pre-hook will deliver the complete cached Map when ready. "
                "Native work can continue."
            )
    elif auth_state == "login_required":
        body = base + (
            "Mapper requires login: run simplicio login google to enable mapping. "
            "No Map was delivered. Native work can continue."
        )
    else:
        body = base + (
            "Mapper authentication is unavailable; no Map was delivered and existing login "
            "data is preserved. Native work can continue."
        )

    # The key excludes host, session, turn, timestamps and local cache hit/miss.
    # A new session receives byte-identical context for the same Map.
    force_delivery = event in {"sessionstart", "session_start"} and (
        hook.get("source") in {"compact", "resume"}
        or not any(hook.get(key) for key in ("session_id", "sessionId", "host_session_id", "conversation_id", "transcript_path"))
    )
    context_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    cache_key = f"simplicio-map-v1:{map_sha}" if map_sha else ""
    try:
        state.mkdir(parents=True, exist_ok=True)
        marker = state / f"mapper-delivery-{delivery_scope()}.json"
        lock = state / "mapper-delivery.lock"
        if not acquire_lock(lock, stale_after=30):
            return ""
        try:
            try:
                prior = json.loads(marker.read_text(encoding="utf-8"))
                if (
                    not force_delivery
                    and prior.get("schema") == "simplicio.mapper-hook-delivery/v1"
                    and prior.get("generation") == generation
                    and prior.get("context_sha256") == context_sha
                ):
                    return ""
            except (OSError, ValueError, TypeError):
                pass
            temporary = marker.with_suffix(".json.tmp")
            temporary.write_text(json.dumps({
                "schema": "simplicio.mapper-hook-delivery/v1",
                "status": "emitted", "generation": generation,
                "map_sha256": map_sha, "map_bytes": map_bytes,
                "context_sha256": context_sha, "cache_key": cache_key,
                "provider_cache_status": "unknown",
            }, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            temporary.replace(marker)
        finally:
            try:
                lock.unlink()
            except OSError:
                pass
    except OSError:
        return ""
    return body


context_events = {
    "sessionstart": "SessionStart",
    "session_start": "SessionStart",
    "userpromptsubmit": "UserPromptSubmit",
    "user_prompt_submit": "UserPromptSubmit",
    "subagentstart": "SubagentStart",
    "subagent_start": "SubagentStart",
}

NATIVE_FILE_TOOLS = {
    "view_file",
    "write_to_file",
    "replace_file_content",
    "read",
    "read_file",
    "write",
    "write_file",
    "edit",
    "strreplace",
    "str_replace",
    "search_replace",
    "file_read",
    "replace",
    "notebookedit",
    "notebook_edit",
    "multiedit",
    "multi_edit",
    "create_file",
    "delete_file",
}


def mcp_profile() -> str:
    explicit = os.environ.get("SIMPLICIO_MCP_PROFILE")
    if explicit is not None and explicit.strip():
        value = explicit.strip().lower().replace("_", "-")
        if value == "mapperonly":
            return "mapper-only"
        if value in {"core", "full", "mapper-only", "diagnostic"}:
            return value
    return "full"


def tool_name_from_hook() -> str:
    return str(
        hook.get("toolName") or hook.get("tool_name") or hook.get("tool") or ""
    ).strip()


def normalize_tool(name: str) -> str:
    n = name.strip().lower().replace("-", "_")
    if n.startswith("functions."):
        n = n.split(".", 1)[1]
    if n.startswith("functions_"):
        n = n[len("functions_") :]
    if "." in n:
        n = n.rsplit(".", 1)[-1]
    return n


def is_runtime_or_third_party(name: str) -> bool:
    n = name.lower()
    return "simplicio" in n or "__" in n or n.startswith("mcp__")


def is_native_file_tool(name: str) -> bool:
    if not name or is_runtime_or_third_party(name):
        return False
    return normalize_tool(name) in NATIVE_FILE_TOOLS


def enforce_disabled() -> bool:
    value = os.environ.get("SIMPLICIO_ENFORCE", "").strip().lower()
    return value in {"0", "false", "off"}


def deny_native_file_tool(name: str) -> None:
    writes = {
        "write_to_file",
        "replace_file_content",
        "write",
        "write_file",
        "edit",
        "strreplace",
        "str_replace",
        "search_replace",
        "replace",
        "notebookedit",
        "notebook_edit",
        "multiedit",
        "multi_edit",
        "create_file",
        "delete_file",
    }
    replacement = (
        "simplicio_edit / simplicio_run"
        if normalize_tool(name) in writes
        else "simplicio_file_read / simplicio_context / simplicio_read_signatures"
    )
    reason = (
        f"MCP profile {mcp_profile()} blocks host-native file tool {name}. "
        f"Use {replacement} after simplicio_map. Third-party MCP/plugins remain allowed."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            separators=(",", ":"),
        )
    )
    print(reason, file=sys.stderr)
    raise SystemExit(2)


if (
    event in {"", "pretooluse", "pre_tool_use", "beforeshellexecution"}
    and mcp_profile() in {"core", "full"}
    and not enforce_disabled()
):
    tool = tool_name_from_hook()
    if is_native_file_tool(tool):
        deny_native_file_tool(tool)

if runtime_mode(repo_from_hook()) == "mapper-only":
    mapper_event = context_events.get(event)
    if event in {"", "pretooluse", "pre_tool_use", "beforeshellexecution"}:
        mapper_event = "PreToolUse"
    if mapper_event:
        root = pathlib.Path(repo_from_hook()).expanduser()
        auth_state = mapper_auth_state(root)
        generation = ""
        if auth_state == "active":
            warmed = warm_context(str(root), verify_content=True)
            if warmed is not None:
                root, generation = warmed
                # Mapping runs to completion in its own bounded worker. A slow
                # repository never makes native host operations wait for it.
                deadline = time.monotonic() + 2
                state = root / ".simplicio" / "hook-context"
                while read_ready_receipt(state, generation, verify_content=True) is None:
                    if not (state / "warm.lock").exists() or time.monotonic() >= deadline:
                        break
                    time.sleep(0.05)
        if os.environ.get("SIMPLICIO_MAPPER_AUTO_CONTEXT") == "1":
            summary = mapper_context_once(root, generation, auth_state)
            if summary:
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": mapper_event, "additionalContext": summary,
                }}, separators=(",", ":")))
    raise SystemExit(0)

if event in context_events:
    warmed = warm_context(repo_from_hook())
    if warmed is not None:
        root, generation = warmed
        summary = compact_summary_once(root, generation)
        if summary:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": context_events[event],
                            "additionalContext": summary,
                        }
                    },
                    separators=(",", ":"),
                )
            )
    raise SystemExit(0)


# Remaining PreToolUse events (shell, third-party MCP, Simplicio tools) pass.
raise SystemExit(0)
PY
