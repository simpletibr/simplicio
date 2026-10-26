#!/usr/bin/env bash
# Creation / edition / measurement, with the three edition shapes the owner asked for:
#   edit_map      -> map the project, then edit a project file
#   edit_codegen  -> change the contract, regenerate the project with codegen
#   edit_loose    -> edit a single file outside any git repository
set -uo pipefail
cd "$(dirname "$0")"

BASE="$PWD/fixture-base"
OUT="$PWD/editbench"
REPS=3
export SIMPLICIO_DAEMON_EXEC=0 SIMPLICIO_TOKIO_DAEMON=0 SIMPLICIO_DISABLE_AUTO_UPDATE=1

rm -rf "$OUT"; mkdir -p "$OUT"
printf 'version\tphase\trep\texit\twall_s\tmaxrss_mb\tbytes\tok\n' >"$OUT/edit.tsv"

# contract edition: same document plus one new field
python3 - <<'PY'
import json
d = json.load(open("api.json"))
d["components"]["schemas"]["Widget"]["properties"]["color"] = {"type": "string"}
json.dump(d, open("api2.json", "w"), indent=1)
PY

PLAN='{"file":"bench_target.rs","operations":[{"op":"replace","find":"pub const A: &str = \"one\";","with":"pub const A: &str = \"ONE\";"},{"op":"insert_after","find":"pub const B: &str = \"two\";","text":"pub const C: &str = \"three\";"}]}'
LOOSE_PLAN='{"file":"loose_target.rs","operations":[{"op":"replace","find":"\"loose\"","with":"\"LOOSE\""}]}'

t() { # version phase rep outfile -- cmd...
  local v="$1" ph="$2" r="$3" out="$4"; shift 4
  [ "$1" = "--" ] && shift
  /usr/bin/time -l "$@" >"$out" 2>"$out.time"
  local code=$?
  local wall rss mb="" bytes
  wall=$(grep -E "^ +[0-9]+\.[0-9]+ real" "$out.time" | awk '{print $1}' | head -1)
  rss=$(grep -E "maximum resident set size" "$out.time" | awk '{print $1}' | head -1)
  [ -n "${rss:-}" ] && mb=$(awk -v b="$rss" 'BEGIN{printf "%.1f", b/1048576}')
  bytes=$(wc -c <"$out" | tr -d ' ')
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$ph" "$r" "$code" "${wall:-}" "${mb:-}" "${bytes:-}" "-" >>"$OUT/edit.tsv"
  return $code
}

mark() { # phase rep ok
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "-" "-" "-" "-" "$4" >>"$OUT/edit.tsv"
}

for v in 3.9.2 3.10.2 main; do
  BIN="$PWD/simplicio-$v"; [ -x "$BIN" ] || continue
  for r in 1 2 3; do
    W="$OUT/w-$v-$r"; rm -rf "$W"; cp -R "$BASE" "$W"
    ( cd "$W" && git init -q && git add -A && git -c user.email=a@b.c -c user.name=b commit -qm seed ) >/dev/null 2>&1

    # 1. creation
    t "$v" create "$r" "$OUT/$v-$r-create.out" -- "$BIN" codegen generate --schema "$PWD/api.json" --lang rust --repo "$W"

    # 2. edition with map: orient first, then edit the project file
    t "$v" edit_map "$r" "$OUT/$v-$r-map.out" -- "$BIN" map --repo "$W" --json
    t "$v" edit_map_apply "$r" "$OUT/$v-$r-emap.out" -- "$BIN" edit "$PLAN" --repo "$W" --json
    if grep -q 'ONE' "$W/bench_target.rs" 2>/dev/null && grep -q 'pub const C' "$W/bench_target.rs" 2>/dev/null; then mark "$v" edit_map_result "$r" "1"; else mark "$v" edit_map_result "$r" "0"; fi

    # 3. edition through codegen: new contract field -> regenerate the project
    t "$v" edit_codegen "$r" "$OUT/$v-$r-ecg.out" -- "$BIN" codegen generate --schema "$PWD/api2.json" --lang rust --repo "$W"
    if grep -rqi 'color' "$W" --include='*.rs' 2>/dev/null; then mark "$v" edit_codegen_result "$r" "1"; else mark "$v" edit_codegen_result "$r" "0"; fi

    # 4. edition of a loose file, outside any repository
    L="$OUT/loose-$v-$r"; rm -rf "$L"; mkdir -p "$L"; printf 'pub const L: &str = "loose";\n' >"$L/loose_target.rs"
    t "$v" edit_loose "$r" "$OUT/$v-$r-eloose.out" -- "$BIN" edit "$LOOSE_PLAN" --repo "$L" --json
    if grep -q 'LOOSE' "$L/loose_target.rs" 2>/dev/null; then mark "$v" edit_loose_result "$r" "1"; else mark "$v" edit_loose_result "$r" "0"; fi

    # 5. measurement
    t "$v" measure "$r" "$OUT/$v-$r-measure.out" -- "$BIN" context --repo "$W" --term memory --json
    rm -rf "$W"
  done
done

# native baseline: same phases without the runtime
for r in 1 2 3; do
  W="$OUT/b-$r"; rm -rf "$W"; cp -R "$BASE" "$W"
  t no-simplicio create "$r" "$OUT/base-$r-create.out" -- bash -c "cat > '$W/created.rs' <<'EOF'
pub fn created() -> u32 { 42 }
EOF"
  t no-simplicio edit_map "$r" "$OUT/base-$r-emap.out" -- bash -c "grep -rn 'pub const A' '$W' >/dev/null; python3 - '$W/bench_target.rs' <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = s.replace('pub const A: &str = \"one\";', 'pub const A: &str = \"ONE\";')
s = s.replace('pub const B: &str = \"two\";', 'pub const B: &str = \"two\";\npub const C: &str = \"three\";')
open(p, 'w').write(s)
PY"
  if grep -q 'ONE' "$W/bench_target.rs" && grep -q 'pub const C' "$W/bench_target.rs"; then mark no-simplicio edit_map_result "$r" "1"; else mark no-simplicio edit_map_result "$r" "0"; fi
  L="$OUT/loose-base-$r"; rm -rf "$L"; mkdir -p "$L"; printf 'pub const L: &str = "loose";\n' >"$L/loose_target.rs"
  t no-simplicio edit_loose "$r" "$OUT/base-$r-eloose.out" -- python3 -c "
import sys
p = sys.argv[1]; s = open(p).read(); open(p, 'w').write(s.replace('\"loose\"', '\"LOOSE\"'))
" "$L/loose_target.rs"
  if grep -q 'LOOSE' "$L/loose_target.rs"; then mark no-simplicio edit_loose_result "$r" "1"; else mark no-simplicio edit_loose_result "$r" "0"; fi
  t no-simplicio measure "$r" "$OUT/base-$r-measure.out" -- bash -c "grep -rn memory '$W' || true; grep -rl memory '$W' | while read -r f; do cat \"\$f\"; done"
  rm -rf "$W"
done

echo done
