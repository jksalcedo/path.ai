import json, pathlib
D = pathlib.Path("app/data")
L = lambda f: json.loads((D / f).read_text(encoding="utf-8"))
heis, cols, sks, progs = L("heis.json")["heis"], L("colleges.json")["colleges"], L("skills.json")["skills"], L("programs.json")["programs"]
hid, cid = {h["id"] for h in heis}, {c["id"] for c in cols}
sk_by_col = {}
for s in sks:
    assert s["college_id"] in cid, f"skill {s['id']} -> bad cluster"
    sk_by_col.setdefault(s["college_id"], set()).add(s["id"])
errs = []
for p in progs:
    if p["college_id"] not in cid: errs.append(f"{p['id']}: bad college_id")
    if not set(p.get("skill_weights", {})) <= sk_by_col.get(p["college_id"], set()):
        errs.append(f"{p['id']}: skill key outside its cluster")
    for w in (p["trait_weights"], p.get("skill_weights", {})):
        if not all(0 <= v <= 3 for v in w.values()): errs.append(f"{p['id']}: weight out of range")
    if not set(p["hei_ids"]) <= hid: errs.append(f"{p['id']}: unknown HEI")
    if not p.get("skill_weights"): errs.append(f"{p['id']}: no skill_weights")
print(f"HEIs {len(heis)} | clusters {len(cols)} | skills {len(sks)} | programs {len(progs)}")
print("skills per cluster:", {k: len(v) for k, v in sk_by_col.items()})
print("ERRORS:", errs or "NONE")