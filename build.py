# Merge data/*.json -> index.html (artifact body) + flags/. Usage: python3 build.py
import json, glob, os, re, sys, shutil, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
D = os.path.dirname(os.path.abspath(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("v", os.path.join(D, "validate.py"))
src = open(os.path.join(D, "validate.py")).read().split("data = json.load")[0]
v = {}; exec(src, v)
out, seen, drop = [], set(), 0
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "data", "*.json"))):
    try: arr = json.load(open(f, encoding="utf-8"))
    except Exception as ex: print("SKIP", f, ex); continue
    for o in arr:
        errs = v["check"](o, 0)
        k = (o.get("sport"), o.get("team"), o.get("season"), o.get("comp"))
        if errs or k in seen: drop += 1; print("DROP", os.path.basename(f), o.get("team"), o.get("season"), errs or "dup"); continue
        seen.add(k); o.pop("date", None)
        for pl in o["p"]: pl[0] = re.sub(r"^([^\W\d_]\.\s*)+", "", pl[0])
        out.append(o)
out.sort(key=lambda o: (o["sport"], o["y"], o["team"]))
os.makedirs(os.path.join(D, "flags"), exist_ok=True)
for cc in sorted({p[2] for o in out for p in o["p"]}):
    dst = os.path.join(D, "flags", cc + ".svg")
    if os.path.exists(dst): continue
    src_f = os.path.expanduser(f"~/Desktop/barjak/flags/{cc}.svg")
    if os.path.exists(src_f): shutil.copy(src_f, dst)
    else:
        try: urllib.request.urlretrieve(f"https://flagcdn.com/{cc}.svg", dst)
        except Exception as ex: print("FLAG MISSING", cc, ex)
js = json.dumps(out, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
html = open(os.path.join(D, "src.html"), encoding="utf-8").read().replace("/*DATA*/[]", js, 1)
open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(html)
fb = sum(o["sport"] == "fb" for o in out)
print(f"built {len(out)} entries (fb {fb}, bb {len(out)-fb}), dropped {drop}, flags {len(os.listdir(os.path.join(D,'flags')))}")
