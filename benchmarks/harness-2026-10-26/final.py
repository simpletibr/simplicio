import csv, json, statistics as st
def load(path):
    try: return list(csv.DictReader(open(path), delimiter="\t"))
    except FileNotFoundError: return []
rows = load("matrix/matrix.tsv") + load("matrix/fix.tsv")
cg = load("matrix/codegen.tsv")
agg = {}
for r in rows:
    agg.setdefault(r["version"], {}).setdefault(r["metric"], []).append(r)
def med(rs, key, cast=float):
    vals = []
    for x in rs:
        v = x.get(key)
        if v in (None, "", "-"): continue
        try: vals.append(cast(v))
        except ValueError: pass
    return round(st.median(vals), 3) if vals else None
out = {}
for v, ms in agg.items():
    out[v] = {}
    for m, rs in ms.items():
        out[v][m] = {"wall_s": med(rs, "wall_s"), "rss_mb": med(rs, "maxrss_mb"), "bytes": med(rs, "bytes", int), "exits": [x["exit"] for x in rs]}
cgagg = {}
for r in cg:
    cgagg.setdefault(r["version"], []).append(r)
for v, rs in cgagg.items():
    out.setdefault(v, {})["codegen"] = {"wall_s": med(rs, "wall_s"), "rss_mb": med(rs, "maxrss_mb"), "bytes": med(rs, "bytes", int), "files": med(rs, "files", int)}
json.dump(out, open("matrix/final.json", "w"), indent=1)
metrics = [("map","map"),("context2","context"),("plan","plan"),("codegen","codegen"),("bench_run","bench_run"),("mcp_cpu","mcp_cpu")]
vs = ["3.9.2","3.10.2","main"]
print(f"{'metric':<12}" + "".join(v.rjust(26) for v in vs))
for key,label in metrics:
    line = label.ljust(12)
    for v in vs:
        e = out.get(v,{}).get(key)
        line += ("-" if not e else f"{e['wall_s']}s {e['rss_mb']}MB {e['bytes']}B").rjust(26)
    print(line)
print("\nbaseline:", json.dumps(out["no-simplicio"], indent=0))
