import json, pathlib
D = pathlib.Path("app/data")
L = lambda f: json.loads((D / f).read_text(encoding="utf-8"))
heis = L("heis.json")["heis"]; cols = L("colleges.json")["colleges"]
skills = L("skills.json")["skills"]; degrees = L("degrees.json")["degrees"]
offerings = L("offerings.json")["offerings"]

hid = {h["id"] for h in heis}
cid = {c["id"] for c in cols}
skills_by_col = {}
for s in skills:
    assert s["college_id"] in cid, f"skill {s['id']} -> unknown college"
    skills_by_col.setdefault(s["college_id"], set()).add(s["id"])

errs, deg_ids, offered, seen = [], set(), set(), set()
for d in degrees:
    deg_ids.add(d["id"])
    if d["college_id"] not in cid: errs.append(f"{d['id']}: unknown college")
    if not set(d.get("skill_weights", {})) <= skills_by_col.get(d["college_id"], set()):
        errs.append(f"{d['id']}: skill key outside its college")
    for w in (d["trait_weights"], d.get("skill_weights", {})):
        if not all(0 <= v <= 3 for v in w.values()): errs.append(f"{d['id']}: weight out of range")

for o in offerings:
    if o["hei_id"] not in hid: errs.append(f"unknown HEI {o['hei_id']}")
    if o["degree_id"] not in deg_ids: errs.append(f"unknown degree {o['degree_id']}")
    key = (o["hei_id"], o["degree_id"], o.get("campus"))
    if key in seen: errs.append(f"duplicate offering {key}")
    seen.add(key); offered.add(o["degree_id"])

orphans = sorted(deg_ids - offered)
print(f"HEIs {len(heis)} | colleges {len(cols)} | skills {len(skills)} | degrees {len(degrees)} | offerings {len(offerings)}")
print("ERRORS:", errs or "NONE")
print("Degrees with no offering:", orphans or "NONE")