set -uo pipefail
cd "$(dirname "$0")"
BASE="$PWD/fixture-base"; OUT="$PWD/matrix"
printf 'version\tmetric\trep\texit\twall_s\tmaxrss_mb\tbytes\tfiles\n' >"$OUT/codegen.tsv"
for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"; [ -x "$BIN" ] || continue
  for r in 1 2 3; do
    W="$OUT/cg-$v-$r"; rm -rf "$W"; cp -R "$BASE" "$W"
    before=$(find "$W" -type f | wc -l | tr -d ' ')
    /usr/bin/time -l "$BIN" codegen generate --schema "$PWD/api.json" --lang rust --repo "$W" >"$OUT/cg-$v-$r.out" 2>"$OUT/cg-$v-$r.time"
    code=$?
    after=$(find "$W" -type f | wc -l | tr -d ' ')
    wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$OUT/cg-$v-$r.time" | awk '{print $1}' | head -1)
    rss=$(grep -E "maximum resident set size" "$OUT/cg-$v-$r.time" | awk '{print $1}' | head -1)
    rss_mb=""; [ -n "${rss:-}" ] && rss_mb=$(awk -v b="$rss" 'BEGIN{printf "%.1f", b/1048576}')
    bytes=$(wc -c <"$OUT/cg-$v-$r.out" | tr -d ' ')
    printf '%s\tcodegen\t%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$r" "$code" "${wall:-}" "${rss_mb:-}" "$bytes" "$((after-before))" >>"$OUT/codegen.tsv"
    rm -rf "$W"
  done
done
cat "$OUT/codegen.tsv"
