#!/usr/bin/env bash
# Version matrix benchmark: v3.9.2 vs v3.10.2 vs main, plus a "no Simplicio" shell baseline.
set -uo pipefail
cd "$(dirname "$0")"

FIXTURE="$PWD/fixture"
TERM="validate_access_token"
OUT="$PWD/results"
rm -rf "$OUT"
mkdir -p "$OUT"

run_timed() { # name, outfile, cmd...
  local name="$1" out="$2"; shift 2
  /usr/bin/time -l "$@" >"$out" 2>"$out.time"
  local code=$?
  local wall rss
  wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$out.time" | awk '{print $1}' | head -1)
  rss=$(grep -E "maximum resident set size" "$out.time" | awk '{print $1}' | head -1)
  printf '%s\t%s\t%s\t%s\n' "$name" "$code" "${wall:-}" "${rss:-}" >>"$OUT/timings.tsv"
}

: >"$OUT/timings.tsv"
printf 'metric\texit\twall_s\tmaxrss_bytes\n' >"$OUT/timings.tsv"

for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"
  [ -x "$BIN" ] || { echo "skip $v (binary missing)"; continue; }
  mkdir -p "$OUT/$v"

  run_timed "$v/map" "$OUT/$v/map.json" "$BIN" map --repo "$FIXTURE" --json
  run_timed "$v/context" "$OUT/$v/context.json" "$BIN" context --repo "$FIXTURE" --term "$TERM" --json
  run_timed "$v/plan" "$OUT/$v/plan.json" "$BIN" plan "fix a null check in src/runtime_auth.rs" --repo "$FIXTURE" --json
  run_timed "$v/benchmark_run" "$OUT/$v/benchmark_run.json" "$BIN" benchmark run --json
  run_timed "$v/benchmark_mcp_cpu" "$OUT/$v/benchmark_mcp_cpu.json" "$BIN" benchmark mcp-cpu --json
done

# ---- baseline: the same questions answered with standard shell tools ----
mkdir -p "$OUT/no-simplicio"
run_timed "no-simplicio/file-list" "$OUT/no-simplicio/file_list.txt" bash -c "find '$FIXTURE' -type f | sort"
run_timed "no-simplicio/grep-term" "$OUT/no-simplicio/grep_term.txt" bash -c "grep -rn '$TERM' '$FIXTURE' || true"
run_timed "no-simplicio/read-matches" "$OUT/no-simplicio/read_matches.txt" bash -c "grep -rl '$TERM' '$FIXTURE' | while read -r f; do cat \"\$f\"; done"

# byte sizes of what each approach hands back
{
  printf 'artifact\tbytes\n'
  for f in "$OUT"/3.9.2/map.json "$OUT"/3.10.2/map.json "$OUT"/main/map.json \
           "$OUT"/3.9.2/context.json "$OUT"/3.10.2/context.json "$OUT"/main/context.json \
           "$OUT"/no-simplicio/file_list.txt "$OUT"/no-simplicio/grep_term.txt "$OUT"/no-simplicio/read_matches.txt; do
    [ -f "$f" ] && printf '%s\t%s\n' "${f#$OUT/}" "$(wc -c <"$f" | tr -d ' ')"
  done
} >"$OUT/bytes.tsv"

echo "done"
cat "$OUT/timings.tsv"
