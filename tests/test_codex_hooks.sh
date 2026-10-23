#!/usr/bin/env bash
# Codex hook gate: the public mcp-route wrappers must forward to the compiled
# Runtime and preserve its decision contract.
#
# The decision itself (Map warming, mapper-only context, native-file-tool
# enforcement) lives in Rust as `simplicio hooks pre-tool` (#6128); these
# wrappers are thin, fail-soft forwarders. The gate therefore needs a compiled
# Runtime: set SIMPLICIO_TEST_BIN, or export SIMPLICIO_BIN, or install one.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/codex/mcp-route.sh"
WINDOWS_HOOK="$ROOT/codex/mcp-route.ps1"
PASS=0
FAIL=0
SKIP=0

TEST_BIN="${SIMPLICIO_TEST_BIN:-${SIMPLICIO_BIN:-}}"
if [ -z "$TEST_BIN" ] && [ -x "${HOME}/.simplicio/bin/simplicio" ]; then
  TEST_BIN="${HOME}/.simplicio/bin/simplicio"
fi
if [ -z "$TEST_BIN" ] || [ ! -x "$TEST_BIN" ]; then
  printf 'FAIL hook gate needs a compiled Runtime: set SIMPLICIO_TEST_BIN=/path/to/simplicio\n' >&2
  exit 1
fi

valid_output() {
  [ -z "$1" ] && return 0
  printf '%s' "$1" | python3 -c '
import json
import sys

value = json.load(sys.stdin)
specific = value.get("hookSpecificOutput") or {}
event = specific.get("hookEventName")
if event == "PreToolUse":
    decision = specific.get("permissionDecision")
    if decision == "allow" and "updatedInput" not in specific:
        raise SystemExit("unsupported permissionDecision:allow without updatedInput")
    if decision == "deny" and not specific.get("permissionDecisionReason"):
        raise SystemExit("PreToolUse deny missing permissionDecisionReason")
    if decision not in {"allow", "deny"}:
        raise SystemExit("unsupported PreToolUse decision")
elif not specific.get("additionalContext"):
    raise SystemExit("hook output has no supported context or decision")
'
}

# run_case <name> <payload> <want_exit> <want_token> [binary]
# want_token __EMPTY__ means the hook must stay silent (allow-unchanged).
run_case() {
  name="$1"
  payload="$2"
  want_exit="$3"
  want_token="$4"
  case_bin="${5:-$TEST_BIN}"
  errfile="$(mktemp)"
  out="$(printf '%s' "$payload" | SIMPLICIO_BIN="$case_bin" bash "$HOOK" 2>"$errfile")"
  got=$?
  err="$(sed -n '1,4p' "$errfile")"
  rm -f "$errfile"

  contract_ok=0
  valid_output "$out" >/dev/null 2>&1 || contract_ok=$?
  token_ok=1
  if [ "$want_token" = "__EMPTY__" ]; then
    [ -z "$out" ] && token_ok=0
  elif printf '%s' "$out" | grep -Fq -- "$want_token"; then
    token_ok=0
  fi

  if [ "$got" = "$want_exit" ] &&
     [ "$contract_ok" -eq 0 ] &&
     [ "$token_ok" -eq 0 ]; then
    printf 'PASS %s\n' "$name"
    PASS=$((PASS + 1))
  else
    printf 'FAIL %s: exit=%s contract=%s output=%s stderr=%s\n' \
      "$name" "$got" "$contract_ok" "$out" "$err" >&2
    FAIL=$((FAIL + 1))
  fi
}

# Core/full native-file-tool enforcement: the Runtime denies when a live MCP
# server is observable, and otherwise prints an explicit UNVERIFIED advisory.
# Both outcomes are enforcement; a silent allow is the failure.
run_enforced_case() {
  name="$1"
  payload="$2"
  token="$3"
  errfile="$(mktemp)"
  out="$(printf '%s' "$payload" | SIMPLICIO_BIN="$TEST_BIN" SIMPLICIO_MCP_PROFILE=full \
    bash "$HOOK" 2>"$errfile")"
  got=$?
  err="$(cat "$errfile")"
  rm -f "$errfile"
  if [ "$got" -eq 2 ] && printf '%s' "$out" | grep -Fq -- "$token"; then
    printf 'PASS %s (denied)\n' "$name"
    PASS=$((PASS + 1))
  elif [ "$got" -eq 0 ] && printf '%s' "$err" | grep -Fq 'mcp_unavailable'; then
    printf 'PASS %s (advisory: no live MCP server on this host)\n' "$name"
    PASS=$((PASS + 1))
  else
    printf 'FAIL %s: exit=%s output=%s stderr=%s\n' "$name" "$got" "$out" "$err" >&2
    FAIL=$((FAIL + 1))
  fi
}

session_repo="$(mktemp -d)"
# Windows Python cannot resolve a Cygwin/MSYS /tmp path, so pass a native path
# in the hook payload while still cleaning up through the shell path.
hook_repo="$session_repo"
if command -v cygpath >/dev/null 2>&1; then
  hook_repo="$(cygpath -m "$session_repo")"
fi
run_case "SessionStart without repository emits bounded bridge context" \
  "{\"hook_event_name\":\"SessionStart\",\"source\":\"startup\",\"cwd\":\"$hook_repo\"}" \
  0 'Simplicio context bridge'
rm -rf -- "$session_repo"
run_case "allow Simplicio tool unchanged" \
  '{"hook_event_name":"PreToolUse","tool_name":"simplicio__simplicio_read","tool_input":{"path":"x"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow native read by default (no profile)" \
  '{"hook_event_name":"PreToolUse","tool_name":"read_file","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow native edit by default (no profile)" \
  '{"hook_event_name":"PreToolUse","tool_name":"write_file","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_enforced_case "enforce native read on core/full" \
  '{"hook_event_name":"PreToolUse","tool_name":"read_file","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  'simplicio_file_read'
run_enforced_case "enforce native edit on core/full" \
  '{"hook_event_name":"PreToolUse","tool_name":"search_replace","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  'simplicio_edit'
run_case "allow native read on mapper-only profile" \
  '{"hook_event_name":"PreToolUse","tool_name":"read_file","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow native shell unchanged" \
  '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git status"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow direct Simplicio shell unchanged" \
  '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"simplicio status --json"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow nested exec_command through functions.exec" \
  '{"hook_event_name":"PreToolUse","tool_name":"functions.exec","tool_input":{"input":"const r = await tools.exec_command({cmd: \"git status\"}); text(r);"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow Simplicio MCP orchestration through functions.exec" \
  '{"hook_event_name":"PreToolUse","tool_name":"functions.exec","tool_input":{"input":"const r = await tools.mcp__simplicio__simplicio_map({repo: \".\"}); text(r);"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow shell wrapper around Simplicio" \
  '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"bash -lc '\''simplicio status --json'\''"},"cwd":"/tmp"}' \
  0 '__EMPTY__'
run_case "allow third-party tool unchanged" \
  '{"hook_event_name":"PreToolUse","tool_name":"mcp__cloudflare__zones_list","tool_input":{}}' \
  0 '__EMPTY__'
run_case "ignore malformed input" 'not-json' 0 '__EMPTY__'
run_case "fail soft when the Runtime binary is missing" \
  '{"hook_event_name":"PreToolUse","tool_name":"read_file","tool_input":{"file_path":"src/main.rs"},"cwd":"/tmp"}' \
  0 '__EMPTY__' /nonexistent

# Wrapper contract: both hosts forward the hook JSON to `hooks pre-tool` and
# keep an empty-stdout allow-unchanged path when the Runtime is absent.
if ! grep -q 'hooks pre-tool' "$HOOK" ||
   ! grep -q 'SIMPLICIO_BIN' "$HOOK" ||
   ! grep -q 'command -v' "$HOOK"; then
  printf 'FAIL shell hook is not the fail-soft forwarder contract\n' >&2
  FAIL=$((FAIL + 1))
else
  printf 'PASS shell hook forwards to hooks pre-tool\n'
  PASS=$((PASS + 1))
fi
if ! grep -q 'hooks pre-tool' "$WINDOWS_HOOK" ||
   ! grep -q 'IsNullOrEmpty($input_json)' "$WINDOWS_HOOK" ||
   ! grep -q 'if (-not $resolved)' "$WINDOWS_HOOK"; then
  printf 'FAIL Windows hook is missing the fail-soft forwarder contract\n' >&2
  FAIL=$((FAIL + 1))
else
  printf 'PASS Windows hook forwards to hooks pre-tool\n'
  PASS=$((PASS + 1))
fi

if command -v pwsh >/dev/null 2>&1; then
  scratch="$(mktemp -d)"
  repo="$scratch/repo"
  fake_bin="$scratch/simplicio-fake"
  mkdir -p "$repo"
  printf '#!/usr/bin/env sh\nexit 0\n' >"$fake_bin"
  chmod 0755 "$fake_bin"
  payload="{\"hookEventName\":\"PreToolUse\",\"toolName\":\"read_file\",\"cwd\":\"$repo\"}"

  default_out="$(printf '%s' "$payload" |
    env SIMPLICIO_BIN="$fake_bin" \
      pwsh -NoLogo -NoProfile -NonInteractive -File "$WINDOWS_HOOK" 2>/dev/null)"
  default_exit=$?
  if [ "$default_exit" -eq 0 ] && [ -z "$default_out" ]; then
    printf 'PASS Windows native read allowed by default\n'
    PASS=$((PASS + 1))
  else
    printf 'FAIL Windows native read allowed by default exit=%s output=%s\n' \
      "$default_exit" "$default_out" >&2
    FAIL=$((FAIL + 1))
  fi

  ps_err="$scratch/ps.err"
  ps_out="$(printf '%s' "$payload" |
    env SIMPLICIO_BIN="$TEST_BIN" SIMPLICIO_MCP_PROFILE=full \
      pwsh -NoLogo -NoProfile -NonInteractive -File "$WINDOWS_HOOK" 2>"$ps_err")"
  ps_exit=$?
  ps_stderr="$(cat "$ps_err" 2>/dev/null || true)"
  rm -rf "$scratch"
  if [ "$ps_exit" -eq 2 ] && printf '%s' "$ps_out" | grep -Fq 'simplicio_file_read'; then
    printf 'PASS Windows native read enforced on core/full (denied)\n'
    PASS=$((PASS + 1))
  elif [ "$ps_exit" -eq 0 ] && printf '%s' "$ps_stderr" | grep -Fq 'mcp_unavailable'; then
    printf 'PASS Windows native read enforced on core/full (advisory)\n'
    PASS=$((PASS + 1))
  else
    printf 'FAIL Windows native read enforced on core/full exit=%s output=%s stderr=%s\n' \
      "$ps_exit" "$ps_out" "$ps_stderr" >&2
    FAIL=$((FAIL + 1))
  fi
else
  printf 'SKIP Windows hook behavior (pwsh unavailable)\n'
  SKIP=$((SKIP + 1))
fi

printf '%s passed, %s failed, %s skipped\n' "$PASS" "$FAIL" "$SKIP"
[ "$FAIL" -eq 0 ]
