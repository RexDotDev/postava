# Build verified EuroLeague 2019-2025 lineups from the official EuroLeague feeds.
# Usage: python3 tools/gen_euroleague.py [--write]   (dry run prints the picks; needs `pip install pycountry`)
# Picks per season (up to PER_SEASON): Final Four, last game of each playoff series, play-in, then regular season.
# Skips team+seasons already in b02_euro.json and Serbian clubs (they belong in cat "srb").
import json, re, sys, random, unicodedata, urllib.request, collections, os
import pycountry

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data", "b02_euro.json")
FEED = "https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/{s}/games"
CACHE = os.environ.get("EL_CACHE", "/tmp/euroleague-cache")
os.makedirs(CACHE, exist_ok=True)

def get(url):
    fn = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]+", "_", url)[-150:] + ".json")
    if os.path.exists(fn): return json.load(open(fn))
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
    json.dump(d, open(fn, "w"))
    return d

# club code -> (English name, kit)
CLUBS = {
    "MAD": ("Real Madrid", ["solid", "#ffffff", "#3d2b8e"]),
    "BAR": ("Barcelona", ["stripes", "#a50044", "#004d98"]),
    "OLY": ("Olympiacos", ["solid", "#d71920", "#ffffff"]),
    "PAN": ("Panathinaikos", ["solid", "#007a3d", "#ffffff"]),
    "ULK": ("Fenerbahçe", ["solid", "#0b1f4b", "#ffd200"]),
    "IST": ("Anadolu Efes", ["solid", "#1b3b8c", "#ffffff"]),
    "CSK": ("CSKA Moscow", ["solid", "#c8102e", "#1a2c6b"]),
    "ZAL": ("Žalgiris", ["solid", "#006a44", "#ffffff"]),
    "TEL": ("Maccabi Tel Aviv", ["solid", "#ffd400", "#0038a8"]),
    "BAS": ("Baskonia", ["solid", "#0a3a8c", "#c8102e"]),
    "MUN": ("Bayern Munich", ["solid", "#dc052d", "#ffffff"]),
    "BER": ("ALBA Berlin", ["solid", "#ffd400", "#0a3a8c"]),
    "MIL": ("Olimpia Milano", ["solid", "#e30613", "#ffffff"]),
    "MCO": ("Monaco", ["solid", "#e30613", "#ffffff"]),
    "VIR": ("Virtus Bologna", ["solid", "#000000", "#ffffff"]),
    "PAM": ("Valencia", ["solid", "#f18a00", "#000000"]),
    "KHI": ("Khimki", ["solid", "#0460b5", "#eccb24"]),
    "DYR": ("Zenit St Petersburg", ["solid", "#0f69b4", "#ffffff"]),
    "UNK": ("UNICS Kazan", ["solid", "#00843d", "#ffffff"]),
    "ASV": ("ASVEL", ["solid", "#007a4d", "#ffffff"]),
    "RED": ("Red Star Belgrade", ["stripes", "#e2001a", "#ffffff"]),
    "PAR": ("Partizan", ["stripes", "#000000", "#ffffff"]),
    "PRS": ("Paris Basketball", ["solid", "#0a0a0a", "#ffffff"]),
    "DUB": ("Dubai Basketball", ["solid", "#0a0a0a", "#c9a44c"]),
    "CAN": ("Gran Canaria", ["solid", "#ffd400", "#0038a8"]),
    "DAR": ("Darüşşafaka", ["solid", "#0b1f4b", "#ffd200"]),
    "BUD": ("Budućnost", ["solid", "#0053a0", "#ffffff"]),
    "HTA": ("Hapoel Tel Aviv", ["solid", "#e30613", "#ffffff"]),
}
SERBIAN = {"RED", "PAR", "BUD"}  # team side goes to cat "srb" (b03), not "euro"
FF_CITY = {2019: "Vitoria-Gasteiz", 2021: "Cologne", 2022: "Belgrade", 2023: "Kaunas", 2024: "Berlin", 2025: "Abu Dhabi"}
SEASONS = ["E2018", "E2019", "E2020", "E2021", "E2022", "E2023", "E2024"]
PER_SEASON = 7
SPECIAL_CC = {"KOS": "xk", "XKX": "xk", "IVO": "ci"}
# national team differs from the passport country the feed reports
CC_OVERRIDE = {"Scottie Wilbekin": "tr", "Shane Larkin": "tr", "Ali Muhammed": "tr", "Jayson Granger": "uy",
               "Nicolas Laprovittola": "ar", "Luis Scola": "ar", "Alex Tyus": "il", "Bryant Dunston": "am",
               "Anthony Randolph": "si", "Leandro Bolmaro": "ar", "Andres Feliz": "do", "Andrés Feliz": "do"}
# add diacritics where the typed answer (key) stays the same
DIA = {"Zizic": "Žižić", "Satoransky": "Satoranský", "Butkevicius": "Butkevičius", "Biberovic": "Biberović",
       "Bertans": "Bertāns", "Strelnieks": "Strēlnieks", "Smits": "Šmits", "Alocen": "Alocén", "Micov": "Micov",
       "Sedekerskis": "Sedekerskis", "Giedraitis": "Giedraitis", "Kalnietis": "Kalnietis"}
IOC = {"SLO": "si", "GER": "de", "NED": "nl", "SUI": "ch", "CRO": "hr", "GRE": "gr", "POR": "pt", "BUL": "bg", "LAT": "lv",
       "DEN": "dk", "RSA": "za", "NGR": "ng", "ANG": "ao", "PUR": "pr", "URU": "uy", "CHI": "cl", "PAR": "py", "PHI": "ph",
       "IRI": "ir", "LIB": "lb", "GUI": "gn", "NIG": "ne", "BAH": "bs", "GAB": "ga", "CGO": "cg", "BUR": "bf", "MAD": "mg",
       "LBA": "ly", "GUA": "gt", "HAI": "ht", "ISV": "vi", "BAR": "bb", "CRC": "cr", "HON": "hn", "ESA": "sv", "MON": "mc",
       "KSA": "sa", "UAE": "ae", "GAM": "gm", "TAN": "tz", "ZIM": "zw", "SUD": "sd", "ALG": "dz", "INA": "id", "MAS": "my",
       "VIE": "vn", "TPE": "tw", "MGL": "mn", "SRI": "lk", "NEP": "np", "BAN": "bd", "KUW": "kw", "OMA": "om", "YEM": "ye"}

def cc3(code):
    if code in SPECIAL_CC: return SPECIAL_CC[code]
    if code in IOC: return IOC[code]
    c = pycountry.countries.get(alpha_3=code)
    if not c: raise SystemExit(f"unknown country {code}")
    if c.alpha_2 == "GB": raise SystemExit("GB player: pick gb-eng/gb-sct/gb-wls/gb-nir by hand")
    return c.alpha_2.lower()

def key(s):
    s = re.sub(r"^([^\W\d_]\.\s*)+", "", s)
    for a, b in (("đ", "dj"), ("Đ", "Dj"), ("ø", "o"), ("æ", "ae"), ("ß", "ss"), ("ł", "l"), ("ı", "i")): s = s.replace(a, b)
    return re.sub(r"[^A-Za-z]", "", unicodedata.normalize("NFD", s)).upper()

# known spellings with diacritics from existing data: normalized key -> (short, full)
KNOWN = {}
import glob
for f in glob.glob(os.path.join(REPO, "data", "b0*.json")):
    for o in json.load(open(f, encoding="utf-8")):
        for sh, full, c in o["p"]: KNOWN.setdefault(key(full), (sh, full, c))

def tc(s):  # title-case an uppercase API name part, keeping Mc/De prefixes readable
    return " ".join("-".join(w[:1].upper() + w[1:].lower() for w in part.split("-")) for part in s.split())

def ovr(full, default):
    for n, c in CC_OVERRIDE.items():
        if key(n) == key(full): return c
    return default

def names(person):
    """-> (short, full, cc or None). Common name from 'name' (SURNAME, FIRST) and the cased abbreviatedName."""
    sur_up, _, first_up = (person.get("name") or "").partition(",")
    abbr = (person.get("abbreviatedName") or "").split(",")[0].strip()
    short = abbr if abbr and not abbr.isupper() else tc(sur_up.strip())
    full = f"{tc(first_up.strip())} {short}".strip()
    if key(full) in KNOWN:
        sh, fu, c = KNOWN[key(full)]
        return sh, fu, ovr(fu, c)
    fixed = DIA.get(short, short)
    if fixed != short:
        full = full[: len(full) - len(short)] + fixed; short = fixed
    return short, full, ovr(full, None)

existing = json.load(open(OUT, encoding="utf-8"))
used = {(o["team"], o["season"]) for o in existing}
new = []
random.seed(2025)

for s in SEASONS:
    yr0 = int(s[1:])
    season = f"{yr0}/{str(yr0 + 1)[2:]}"
    games = [g for g in get(FEED.format(s=s) + "?limit=500")["data"] if g.get("status") == "result"]
    for g in games: g["_y"] = int(g["date"][:4])
    games = [g for g in games if 2019 <= g["_y"] <= 2025]
    # playoff series results between pairs
    series = collections.defaultdict(lambda: collections.Counter())
    last_po = {}
    for g in sorted([g for g in games if g["phaseType"]["code"] == "PO"], key=lambda g: g["date"]):
        h, a = g["home"]["code"], g["away"]["code"]
        pair = frozenset((h, a)); w = h if g["home"]["score"] > g["away"]["score"] else a
        series[pair][w] += 1; last_po[pair] = g["code"]
    ff = sorted([g for g in games if g["phaseType"]["code"] == "FF"], key=lambda g: g["date"])
    po_last = [g for g in games if g["phaseType"]["code"] == "PO" and last_po.get(frozenset((g["home"]["code"], g["away"]["code"]))) == g["code"]]
    pi = [g for g in games if g["phaseType"]["code"] == "PI"]
    rs = [g for g in games if g["phaseType"]["code"] == "RS"]
    random.shuffle(rs)
    big = {"MAD", "BAR", "OLY", "PAN", "ULK", "IST", "CSK", "ZAL", "TEL", "MIL", "MCO", "BAS", "MUN", "VIR"}
    rs.sort(key=lambda g: -((g["home"]["code"] in big) + (g["away"]["code"] in big)))
    cands = ff + po_last + pi + rs
    picked = 0
    for g in cands:
        if picked >= PER_SEASON: break
        for side, other in (("home", "away"), ("away", "home")):
            if picked >= PER_SEASON: break
            code, ocode = g[side]["code"], g[other]["code"]
            if code in SERBIAN or code not in CLUBS or ocode not in CLUBS: continue
            team, kit = CLUBS[code]; opp, okit = CLUBS[ocode]
            if (team, season) in used: continue
            ph = g["phaseType"]["code"]
            # final four: which game?
            if ph == "FF":
                idx = ff.index(g); fcount = len(ff)
                kind = "semi-final" if idx < 2 else ("3rd place game" if (fcount == 4 and idx == 2) else "final")
                comp = f"EuroLeague, Final Four, {kind}"
            elif ph == "PO":
                comp = f"EuroLeague, playoffs, Game {sum(series[frozenset((code, ocode))].values())}"
            elif ph == "PI":
                comp = "EuroLeague, play-in"
            else:
                comp = f"EuroLeague, round {g['round']['round']}"
            st = get(FEED.format(s=s) + f"/{g['code']}/stats")
            box = st["local"] if side == "home" else st["road"]
            starters = [p for p in box["players"] if p["stats"].get("startFive")]
            if len(starters) != 5: print("SKIP not 5 starters", s, g["code"], team); continue
            starters.sort(key=lambda p: (p["player"].get("position") or 2, p["player"]["person"].get("height") or 0))
            plist = []
            for p in starters:
                sh, full, c = names(p["player"]["person"])
                c = c or cc3(p["player"]["person"]["country"]["code"])
                if c in ("rs", "hr", "ba", "me") and re.search(r"ic$", sh):  # ex-YU surnames: -ic -> -ić
                    full = full[: len(full) - len(sh)] + sh[:-1] + "ć"; sh = sh[:-1] + "ć"
                plist.append([sh, full, c])
            if any(not 3 <= len(key(p[0])) <= 18 for p in plist): print("SKIP short name", plist); continue
            my, their = g[side]["score"], g[other]["score"]
            ot = any(g[side]["quarters"].get(f"ot{i}") is not None for i in range(1, 6))
            score = f"{my}-{their}" + (" OT" if ot else "")
            won = my > their
            note = None
            city = FF_CITY.get(g["_y"])
            if ph == "FF" and city:
                note = {("final", True): f"{city}: EuroLeague champions", ("final", False): f"{city}: runners-up",
                        ("semi-final", False): f"Final Four in {city}: out in the semi-final",
                        ("semi-final", True): f"Final Four in {city}: through to the final",
                        ("3rd place game", True): f"Final Four in {city}: third place",
                        ("3rd place game", False): f"Final Four in {city}: fourth place"}[(kind, won)]
            elif ph == "PO":
                c = series[frozenset((code, ocode))]; w, l = c[code], c[ocode]
                note = f"{'Won' if won else 'Lost'} the playoff series {max(w, l)}-{min(w, l)}"
            elif s == "E2019":
                note = "Season cancelled in March 2020 because of the pandemic"
            o = {"sport": "bb", "cat": "euro", "team": team, "opp": opp, "score": score, "comp": comp,
                 "season": season, "y": g["_y"]}
            if note: o["note"] = note
            o.update({"form": "5", "kit": kit, "okit": okit, "p": plist, "src": f"euroleague {s} game {g['code']}"})
            new.append(o); used.add((team, season)); picked += 1
            print(f"{s} #{g['code']:>3} {ph} {team} {score} {opp} | {comp} | {note or ''} | {', '.join(p[0]+'('+p[2]+')' for p in plist)}")

print(len(new), "new entries")
if "--write" in sys.argv:
    for o in new: o.pop("src")
    json.dump(existing + new, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", OUT)
