#!/usr/bin/env bash
# Clean version matrix: v3.9.2 / v3.10.2 / main  + shell baseline.
# Each rep gets a fresh copy of the fixture (git-init) so no lock/cache leaks.
set -uo pipefail
cd "$(dirname "$0")"

BASE="$PWD/fixture-base"
OUT="$PWD/matrix"
REPS="${REPS:-3}"
TERM="validate_access_token"
export SIMPLICIO_DAEMON_EXEC=0
export SIMPLICIO_TOKIO_DAEMON=0
export SIMPLICIO_DISABLE_AUTO_UPDATE=1

rm -rf "$OUT"; mkdir -p "$OUT"
printf 'version\tmetric\trep\texit\twall_s\tmaxrss_mb\tbytes\n' >"$OUT/matrix.tsv"

time_cmd() { # version metric rep outfile cmd...
  local v="$1" m="$2" r="$3" out="$4"; shift 4
  /usr/bin/time -l "$@" >"$out" 2>"$out.time"
  local code=$?
  local wall rss
  wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$out.time" | awk '{print $1}' | head -1)
  rss=$(grep -E "maximum resident set size" "$out.time" | awk '{print $1}' | head -1)
  local rss_mb=""
  [ -n "$rss" ] && rss_mb=$(awk -v b="$rss" 'BEGIN{printf "%.1f", b/1048576}')
  local bytes
  bytes=$(wc -c <"$out" 2>/dev/null | tr -d ' ')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$m" "$r" "$code" "${wall:-}" "${rss_mb:-}" "${bytes:-}" >>"$OUT/matrix.tsv"
}

for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"
  [ -x "$BIN" ] || continue
  for r in $(seq 1 "$REPS"); do
    W="$OUT/work-$v-$r"
    rm -rf "$W"; cp -R "$BASE" "$W"
    ( cd "$W" && git init -q && git add -A && git -c user.email=a@b.c -c user.name=b commit -qm seed ) >/dev/null 2>&1
    mkdir -p "$OUT/$v/rep$r"
    time_cmd "$v" "map" "$r" "$OUT/$v/rep$r/map.json" "$BIN" map --repo "$W" --json
    time_cmd "$v" "context" "$r" "$OUT/$v/rep$r/context.json" "$BIN" context --repo "$W" --term "$TERM" --json
    time_cmd "$v" "plan" "$r" "$OUT/$v/rep$r/plan.json" "$BIN" plan "fix a null check in runtime_auth" --repo "$W" --json
    time_cmd "$v" "codegen" "$r" "$OUT/$v/rep$r/codegen.json" "$BIN" codegen generate --schema "$BASE/../api.json" --lang rust --out "$W/generated" --json
    time_cmd "$v" "bench_run" "$r" "$OUT/$v/rep$r/bench.json" "$BIN" benchmark run --json
    time_cmd "$v" "mcp_cpu" "$r" "$OUT/$v/rep$r/mcp_cpu.json" "$BIN" benchmark mcp-cpu --json
    pkill -f "bench-versions/simplicio-$v.*daemon" 2>/dev/null
    rm -rf "$W"
  done
done

# shell baseline on a fresh copy
for r in $(seq 1 "$REPS"); do
  W="$OUT/work-base-$r"; rm -rf "$W"; cp -R "$BASE" "$W"
  mkdir -p "$OUT/no-simplicio/rep$r"
  time_cmd "no-simplicio" "file_list" "$r" "$OUT/no-simplicio/rep$r/list.txt" bash -c "find '$W' -type f | sort"
  time_cmd "no-simplicio" "grep_term" "$r" "$OUT/no-simplicio/rep$r/grep.txt" bash -c "grep -rn '$TERM' '$W' || true"
  time_cmd "no-simplicio" "read_matches" "$r" "$OUT/no-simplicio/rep$r/cat.txt" bash -c "grep -rl '$TERM' '$W' | while read -r f; do cat \"\$f\"; done"
  rm -rf "$W"
done

echo "done"
