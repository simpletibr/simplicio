import csv, json, statistics as st
rows = list(csv.DictReader(open("matrix/matrix.tsv"), delimiter="\t"))
agg = {}
for r in rows:
    key = (r["version"], r["metric"])
    agg.setdefault(key, []).append(r)
out = {}
for (v, m), rs in agg.items():
    walls = [float(x["wall_s"]) for x in rs if x["wall_s"]]
    rss = [float(x["maxrss_mb"]) for x in rs if x["maxrss_mb"]]
    byt = [int(x["bytes"]) for x in rs if x["bytes"]]
    exits = [x["exit"] for x in rs]
    out.setdefault(v, {})[m] = {
        "reps": len(rs), "exits": exits,
        "wall_s_median": round(st.median(walls), 3) if walls else None,
        "rss_mb_median": round(st.median(rss), 1) if rss else None,
        "bytes_median": int(st.median(byt)) if byt else None,
    }
json.dump(out, open("matrix/summary.json", "w"), indent=1)
metrics = ["map", "context", "plan", "codegen", "bench_run", "mcp_cpu"]
versions = ["3.9.2", "3.10.2", "main", "no-simplicio"]
print("metric".ljust(14) + "".join(v.rjust(16) for v in versions))
for m in metrics:
    line = m.ljust(14)
    for v in versions:
        e = out.get(v, {}).get(m)
        if not e: line += "-".rjust(16); continue
        ok = all(x == "0" for x in e["exits"])
        cell = f"{e['wall_s_median']}s {e['rss_mb_median']}MB"
        line += (("" if ok else "!") + cell).rjust(16)
    print(line)
for m in ["file_list", "grep_term", "read_matches"]:
    e = out["no-simplicio"][m]
    print(m.ljust(14), f"{e['wall_s_median']}s {e['rss_mb_median']}MB {e['bytes_median']}B")
