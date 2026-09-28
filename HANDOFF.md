# POSTAVA — handoff

Wordle-style "guess the starting lineup" game (like playfootball.games/missing-11), Serbian Latin UI.
Football from 2009 (clubs, national teams, Zvezda/Partizan/Vojvodina, Serbia), basketball from 2012 (NBA, EuroLeague, Serbia NT + Serbian clubs).
Goal: 500+ football lineups + ~155 basketball.

## Files
- `src.html` — the whole game (UI + logic). Data is injected at `/*DATA*/[]`.
- `build.py` — merges `data/*.json`, validates, drops bad/dup entries, strips leading initials ("V. Milinković-Savić" → "Milinković-Savić"), fetches missing flags (flagcdn.com) into `flags/`, writes `index.html`.
- `validate.py <file>` — schema check (run on every data file).
- `SPEC.md` — data schema + quality rules. Every data agent must read it.
- `index.html` — built artifact body (no <html>/<head>: the Artifact publisher wraps it). For a standalone/GitHub Pages copy, prepend `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">`.
- `flags/<cc>.svg` — nationality flags referenced as relative `flags/xx.svg`.

Build: `python3 build.py` → prints `built N entries (fb X, bb Y)`.

## Published
Artifact (private, claude.ai): https://claude.ai/artifact/WB1nNKgdRTwnA2GVmXNK6h (v1, 330 entries). Republish: Artifact publish with `url`, `file_path` = index.html, `files` = every `flags/*.svg` mapped to itself.

## Data status (341 entries built)
DONE (in `data/`, verified against box scores / Wikipedia / ESPN / Opta):
| file | scope | n |
|---|---|---|
| b01_nba.json | NBA starting fives 2012–2025 | 55 |
| b02_euro.json | EuroLeague 2012–2025 (no Serbian clubs) | 50 |
| b03_srb.json | Serbia basketball NT + opponents + Zvezda/Partizan/Mega | 50 |
| f09_wc.json | World Cups 2010–2022 + famous qualifiers (no Serbia) | 60 |
| f10_euro_copa.json | Euros, Copa América, AFCON, Nations League, Asian Cup, Gold Cup, Olympics (no Serbia) | 60 |
| f12_srb_nat.json | Serbia football NT (+U20 2015, U19 2013) | 11 |
| f04_partial.json | English non-big-six clubs, PARTIAL (44 of 55) | 44 |

MISSING — generate each with one agent (prompt: "Read SPEC.md and follow it exactly. Scope: … Target N. Output data/<file>. Run validate.py until OK."):
| file | scope | target |
|---|---|---|
| f01_ucl.json | UEFA Champions League only, 2009/10–2024/25: both finalists of every final 2010–2025 + legendary nights (Barça 6-1 PSG, Liverpool 4-0 Barça, Ajax 2019, Roma 3-0 Barça, Monaco 2017, APOEL 2012, Dortmund 4-1 Real 2013, Atalanta 2020, Villarreal 2022…). No Serbian clubs as "team". | 60 |
| f02_uel.json | Europa League, Conference League, UEFA Super Cup, Club World Cup, 2009–2025: both finalists of every UEL final 2010–2025 and UECL finals 2022–2025 + famous nights (Liverpool 4-3 Dortmund 2016, Eintracht at Barça 2022…). No Serbian clubs. | 55 |
| f03_eng_big.json | Man Utd, Man City, Liverpool, Chelsea, Arsenal, Tottenham — DOMESTIC only (PL, FA Cup, League Cup, Community Shield), ~9 per club across many seasons (City 3-2 QPR 2012, Utd 8-2 Arsenal, City 6-1 Utd, Liverpool 13/14, 19/20, Chelsea 16/17 3-4-3, Spurs 16/17, Arteta's Arsenal, Slot's Liverpool 24/25…). | 55 |
| f04_eng_cult.json | English clubs outside the big six, domestic only. REST of scope: 11 more beyond f04_partial.json (check it to avoid duplicates). Must cover: Leicester 15/16, Everton Moyes/Martínez (Baines, Coleman, Barkley, Lukaku), West Ham (Payet 15/16, Lingard 20/21), Southampton, Swansea 2013 League Cup, Stoke Pulis, Wigan 2013 FA Cup, Newcastle 11/12, Blackpool 10/11, Leeds Bielsa, Sheffield Utd 19/20, Wolves, Burnley, Brighton, Villa Emery, Forest 24/25, Bradford 2013, Birmingham 2011. | 11 |
| f05_esp.json | Spanish clubs, DOMESTIC only (La Liga, Copa, Supercopa): Barça 5-0 Real 2010, Real 11/12, Atlético 13/14 decider, Valencia (Emery era; 2019 Copa with Rodrigo, Garay, Parejo, Gayà), Sevilla, Villarreal, Málaga 12/13, Athletic Bielsa, Real Sociedad, Betis 2022, Girona 23/24, Celta, Getafe, Levante, Eibar, Depor, Osasuna 2023, Mallorca 2025. | 55 |
| f06_ita.json | Italian clubs, DOMESTIC only: Inter 09/10, Milan 10/11 & 21/22, Juve Conte/Allegri, Napoli Mazzarri/Sarri/Spalletti, Roma, Lazio, Atalanta Gasperini, Fiorentina, Udinese, Sampdoria 09/10, Palermo, Torino, Sassuolo, Bologna 2025 Coppa, Verona, Empoli. | 55 |
| f07_ger_fra.json | German + French clubs, DOMESTIC only: Dortmund Klopp (2012 Pokal 5-2), Bayern, Leverkusen 23/24, Stuttgart, Leipzig, Gladbach, Schalke, Wolfsburg 2009, Hoffenheim, Eintracht 2018 Pokal, Union; Marseille 09/10, Lille 10/11 & 20/21, Montpellier 11/12, PSG eras, Monaco 16/17, Lyon, Nice, Lens 22/23, Brest 23/24. | 55 |
| f08_rest.json | Clubs outside ENG/ESP/ITA/GER/FRA/SRB, domestic or non-UEFA competitions (Ajax, PSV, Feyenoord, Porto AVB, Benfica, Sporting, Celtic, Rangers, Galatasaray, Fenerbahçe, Shakhtar, Zenit, Olympiacos, Dinamo Zagreb, Salzburg, Basel, Boca, River 2015/2018, Corinthians 2012, Santos 2011, Flamengo 2019, Palmeiras, Atlético Nacional 2016, LA Galaxy, Inter Miami, Al-Nassr…), max ~2 per club. | 60 |
| f11_srb_clubs.json | cat "srb": Crvena zvezda ~20, Partizan ~18, Vojvodina ~8, all competitions 2009–2025 (Zvezda 2-0 Liverpool 2018, CL 2019/20 & 2023/24, Partizan CL 2010/11, EL vs Plzeň 2018, Vojvodina 4-0 Sampdoria 2015, Kup Srbije finals, derbies). EVERY lineup must be verified on the web. | 45 |

Before generating a missing file, `git pull` — the local session may still push some of these (agents were still running at handoff).
Web-search quota ran out for some local agents; direct page fetches (Wikipedia match articles, ESPN, worldfootball.net, transfermarkt) worked as fallback.

## Game rules implemented
- Per player: Wordle grid, length = letters of the known name (diacritics stripped, đ→DJ, spaces/hyphens removed), 6 tries (4 in "Teško", which also hides flags).
- Duplicate surnames in one lineup are allowed (both shirts accept the same answer).
- Random deck without repeats per sport/category (localStorage), "Dnevna" = daily puzzle seeded by date, stats, share text.

## Possible next steps
- Finish missing data (above), rebuild, republish artifact.
- Spot-check left/right order in a few lineups (agents flagged formation/side doubts, never player identity).
- Optional: GitHub Pages (make repo public, add full `<head>` wrapper as `index.html`).
