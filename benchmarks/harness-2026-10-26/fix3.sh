set -uo pipefail
cd "$(dirname "$0")"
BASE="$PWD/fixture-base"; OUT="$PWD/matrix"; TERM="memory"; REPS=3
export SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 SIMPLICIO_DISABLE_AUTO_UPDATE=1
printf 'version\tmetric\trep\texit\twall_s\tmaxrss_mb\tbytes\n' >"$OUT/fix.tsv"
time_cmd() { local v="$1" m="$2" r="$3" out="$4"; shift 4
  /usr/bin/time -l "$@" >"$out" 2>"$out.time"; local code=$?
  local wall rss rss_mb="" bytes
  wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$out.time" | awk '{print $1}' | head -1)
  rss=$(grep -E "maximum resident set size" "$out.time" | awk '{print $1}' )
  [ -n "${rss:-}" ] && rss_mb=$(awk -v b="$rss" 'BEGIN{printf "%.1f", b/1048576}')
  bytes=$(wc -c <"$out" 2>/dev/null | tr -d ' ')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$m" "$r" "$code" "${wall:-}" "${rss_mb:-}" "${bytes:-}" >>"$OUT/fix.tsv"
}
for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"; [ -x "$BIN" ] || continue
  for r in 1 2 3; do
    W="$OUT/fix-$v-$r"; rm -rf "$W"; cp -R "$BASE" "$W"; ( cd "$W" && git init -q && git add -A && git -c user.email=a@b.c -c user.name=b commit -qm seed ) >/dev/null 2>&1
    time_cmd "$v" context2 "$r" "$OUT/$v/rep$r/context2.json" "$BIN" context --repo "$W" --term "$TERM" --json
    time_cmd "$v" codegen2 "$r" "$OUT/$v/rep$r/codegen2.json" "$BIN" codegen generate --schema "$PWD/api.json" --lang rust --repo "$W" --json
    printf '%s\tgenerated_files\t%s\t0\t-\t-\t%s\n' "$v" "$r" "$(find "$W" -newer "$PWD/api.json" -type f 2>/dev/null | wc -l | tr -d ' ')" >>"$OUT/fix.tsv"
    rm -rf "$W"
  done
done
for r in 1 2 3; do
  W="$OUT/fix-base-$r"; rm -rf "$W"; cp -R "$BASE" "$W"; mkdir -p "$OUT/no-simplicio/rep$r"
  time_cmd "no-simplicio" "grep_term2" "$r" "$OUT/no-simplicio/rep$r/grep2.txt" bash -c "grep -rn '$TERM' '$W' || true"
  time_cmd "no-simplicio" "read_matches2" "$r" "$OUT/no-simplicio/rep$r/cat2.txt" bash -c "grep -rl '$TERM' '$W' | while read -r f; do cat \"\$f\"; done"
  rm -rf "$W"
done
echo done
