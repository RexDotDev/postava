import json, sys, re, unicodedata
PAT = {"solid","stripes","hoops","halves","sash","sleeves","pinstripes","quarters","checks","chevron","band"}
CC = re.compile(r"^([a-z]{2}|gb-(eng|sct|wls|nir))$")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
def key(s):
    s = re.sub(r"^([^\W\d_]\.\s*)+", "", s)
    s = s.replace("đ","dj").replace("Đ","Dj").replace("ø","o").replace("Ø","O").replace("æ","ae").replace("ß","ss").replace("ł","l").replace("Ł","L").replace("ı","i").replace("ð","d").replace("þ","th")
    s = unicodedata.normalize("NFD", s)
    return re.sub(r"[^A-Za-z]", "", s).upper()
def check(o, i):
    e = []
    for f in ("sport","cat","team","opp","score","comp","season","y","form","kit","okit","p"):
        if f not in o: e.append(f"missing {f}")
    if e: return e
    sp = o["sport"]
    if sp not in ("fb","bb"): e.append("bad sport")
    if o["cat"] not in ({"club","nat","srb"} if sp=="fb" else {"nba","euro","srb"}): e.append("bad cat")
    if not isinstance(o["y"], int) or not (2009 if sp=="fb" else 2012) <= o["y"] <= 2026: e.append("bad y")
    for k in ("kit","okit"):
        v = o[k]
        if not (isinstance(v,list) and len(v)==3 and v[0] in PAT and HEX.match(v[1]) and HEX.match(v[2])): e.append(f"bad {k} {v}")
    if len(o.get("note","")) > 90: e.append("note too long")
    p = o["p"]
    if sp=="fb":
        try: lines = [int(x) for x in o["form"].split("-")]
        except: lines = []
        if sum(lines)!=10: e.append(f"form {o['form']} doesn't sum to 10")
        if len(p)!=11: e.append(f"{len(p)} players, need 11")
    else:
        if o["form"]!="5": e.append("bb form must be '5'")
        if len(p)!=5: e.append(f"{len(p)} players, need 5")
    keys = []
    for pl in p:
        if not (isinstance(pl,list) and len(pl)==3): e.append(f"bad player {pl}"); continue
        k = key(pl[0])
        if not 3 <= len(k) <= 18: e.append(f"short '{pl[0]}' -> {k} length {len(k)}")
        if not CC.match(pl[2]): e.append(f"bad cc {pl[2]} for {pl[0]}")
        keys.append(k)
    note = o.get("note","").lower()
    for pl in p:
        if isinstance(pl,list) and len(pl)==3 and len(pl[0])>3 and pl[0].lower() in note: e.append(f"note mentions {pl[0]}")
    return e
data = json.load(open(sys.argv[1], encoding="utf-8"))
bad = 0; seen = set()
for i,o in enumerate(data):
    errs = check(o,i)
    ts = (o.get("team"), o.get("season"))
    if ts in seen: errs.append(f"duplicate team+season {ts}")
    seen.add(ts)
    if errs: bad += 1; print(f"#{i} {o.get('team')} {o.get('season')}: " + "; ".join(errs))
print(f"{len(data)} entries, {bad} with errors" if bad else f"OK {len(data)} entries")
sys.exit(1 if bad else 0)
