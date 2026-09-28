# Merge data/*.json -> index.html + data.<hash>.json (standalone site for GitHub Pages / Vercel),
# artifact.html (Artifact body, data inlined) + flags/.   Usage: python3 build.py
import json, glob, os, re, sys, shutil, urllib.request, hashlib, html as htmlmod
# Public address of the site. Link previews (Open Graph) need absolute image URLs, so set this once the
# domain is known, e.g. "https://squads.vercel.app", and rebuild. Empty = relative URLs (previews may lack the image).
SITE_URL = os.environ.get("SITE_URL", "https://postava-beta.vercel.app").rstrip("/")
sys.path.insert(0, os.path.dirname(__file__))
D = os.path.dirname(os.path.abspath(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("v", os.path.join(D, "validate.py"))
src = open(os.path.join(D, "validate.py")).read().split("data = json.load")[0]
v = {}; exec(src, v)
# Per-category year window, e.g. EuroLeague only 2019–2025 (the data files keep older entries)
YEARS = {("bb", "euro"): (2019, 2025)}
out, seen, drop, skip = [], set(), 0, 0
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "data", "*.json"))):
    try: arr = json.load(open(f, encoding="utf-8"))
    except Exception as ex: print("SKIP", f, ex); continue
    for o in arr:
        lo, hi = YEARS.get((o.get("sport"), o.get("cat")), (0, 9999))
        if not lo <= o.get("y", 0) <= hi: skip += 1; continue
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
tpl = open(os.path.join(D, "src.html"), encoding="utf-8").read()
MARK = "<script>\nconst DATA = /*DATA*/[];"
assert MARK in tpl, "src.html must start its script with: " + MARK
# Artifact: data inlined (one self-contained page; the Artifact publisher adds <html>/<head>)
open(os.path.join(D, "artifact.html"), "w", encoding="utf-8").write(tpl.replace("/*DATA*/[]", js, 1))
# Site: data in its own content-hashed file, so browsers can cache it for good and only refetch when it changes
blob = json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
data_name = f"data.{hashlib.sha1(blob).hexdigest()[:10]}.json"
for old in glob.glob(os.path.join(D, "data.*.json")):
    if os.path.basename(old) != data_name: os.remove(old)
open(os.path.join(D, data_name), "wb").write(blob)
loader = ("<script type=\"module\">\n"
          f"const DATA = await fetch('{data_name}').then(r => {{ if (!r.ok) throw new Error(r.status); return r.json(); }})\n"
          "  .catch(err => { document.getElementById('match').innerHTML = '<div class=\"comp\">Could not load the lineups. Please reload.</div>'; throw err; });")
body = tpl.replace(MARK, loader, 1)
cut = body.index("</style>") + len("</style>")
desc = "Guess the real starting lineup of famous football and basketball matches. Real games, real starting XIs."
url = lambda p: f"{SITE_URL}/{p}" if SITE_URL else p
e = htmlmod.escape
head = ('<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        f'<meta name="description" content="{e(desc)}">\n'
        '<meta name="theme-color" content="#0d1524">\n'
        '<link rel="icon" href="icon.svg" type="image/svg+xml">\n'
        '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
        '<link rel="manifest" href="site.webmanifest">\n'
        f'<link rel="preload" href="{data_name}" as="fetch" crossorigin>\n'
        + (f'<link rel="canonical" href="{SITE_URL}/">\n<meta property="og:url" content="{SITE_URL}/">\n' if SITE_URL else "")
        + '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="Squads">\n'
        '<meta property="og:title" content="Squads: guess the starting lineup">\n'
        f'<meta property="og:description" content="{e(desc)}">\n'
        f'<meta property="og:image" content="{url("og.png")}">\n'
        '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="Squads: a football pitch with shirts and dashes for each player name">\n'
        '<meta name="twitter:card" content="summary_large_image">\n')
page = f'<!doctype html>\n<html lang="en">\n<head>\n{head}{body[:cut]}\n</head>\n<body>\n{body[cut:]}\n</body>\n</html>\n'
open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(page)
fb = sum(o["sport"] == "fb" for o in out)
print(f"built {len(out)} entries (fb {fb}, bb {len(out)-fb}), dropped {drop}, outside year window {skip}, flags {len(os.listdir(os.path.join(D,'flags')))}")
