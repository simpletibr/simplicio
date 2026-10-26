set -uo pipefail
cd "$(dirname "$0")"
BASE="$PWD/fixture-base"; OUT="$PWD/cem"; REPS=3
export SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 SIMPLICIO_DISABLE_AUTO_UPDATE=1
rm -rf "$OUT"; mkdir -p "$OUT"
printf 'version\tphase\trep\texit\twall_s\tmaxrss_mb\tbytes\n' >"$OUT/cem.tsv"
PLAN='{"file":"bench_target.rs","operations":[{"op":"replace","find":"pub const A: &str = \"one\";","with":"pub const A: &str = \"ONE\";"},{"op":"insert_after","find":"pub const B: &str = \"two\";","text":"pub const C: &str = \"three\";"}]}'
t() { local v="$1" ph="$2" r="$3" out="$4"; shift 4
  /usr/bin/time -l "$@" >"$out" 2>"$out.time"; local c=$?
  local wall rss mb="" bytes
  wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$out.time" | awk '{print $1}' | head -1)
  rss=$(grep -E "maximum resident set size" "$out.time" | awk '{print $1}' | head -1)
  [ -n "${rss:-}" ] && mb=$(awk -v b="$rss" 'BEGIN{printf "%.1f", b/1048576}')
  bytes=$(wc -c <"$out" | tr -d ' ')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$ph" "$r" "$c" "${wall:-}" "${mb:-}" "${bytes:-}" >>"$OUT/cem.tsv"
}
for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"; [ -x "$BIN" ] || continue
  for r in 1 2 3; do
    W="$OUT/w-$v-$r"; rm -rf "$W"; cp -R "$BASE" "$W"; ( cd "$W" && git init -q && git add -A && git -c user.email=a@b.c -c user.name=b commit -qm seed ) >/dev/null 2>&1
    t "$v" create "$r" "$OUT/$v-$r-create.out" "$BIN" codegen generate --schema "$PWD/api.json" --lang rust --repo "$W"
    t "$v" edit "$r" "$OUT/$v-$r-edit.out" "$BIN" edit "$PLAN" --repo "$W" --json
    sed -n '1,3p' "$W/bench_target.rs" >"$OUT/$v-$r-edit.result"
    t "$v" measure "$r" "$OUT/$v-$r-measure.out" "$BIN" context --repo "$W" --term memory --json
    rm -rf "$W"
  done
done
# native baseline: create with heredoc, edit with python, measure with grep+cat
for r in 1 2 3; do
  W="$OUT/b-$r"; rm -rf "$W"; cp -R "$BASE" "$W"
  t no-simplicio create "$r" "$OUT/base-$r-create.out" bash -c "cat > '$W/created.rs' <<'EOF'
pub fn created() -> u32 { 42 }
EOF"
  t no-simplicio edit "$r" "$OUT/base-$r-edit.out" python3 - "$W/bench_target.rs" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = s.replace('pub const A: &str = "one";', 'pub const A: &str = "ONE";')
s = s.replace('pub const B: &str = "two";', 'pub const B: &str = "two";\npub const C: &str = "three";')
open(p, "w").write(s)
PY
  sed -n '1,3p' "$W/bench_target.rs" >"$OUT/base-$r-edit.result"
  t no-simplicio measure "$r" "$OUT/base-$r-measure.out" bash -c "grep -rn memory '$W' || true; grep -rl memory '$W' | while read -r f; do cat \"\$f\"; done"
  rm -rf "$W"
done
echo done
cat "$OUT/cem.tsv"
