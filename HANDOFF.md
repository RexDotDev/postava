# SQUADS — handoff (repo: postava)

Wordle-style "guess the starting lineup" game (like playfootball.games/missing-11), called **Squads**. UI and all data text (comp, note, team names) are in English.
Football from 2009 (clubs, national teams, Red Star/Partizan/Vojvodina, Serbia), basketball from 2012 (NBA, Serbia NT + Serbian clubs) and EuroLeague 2019–2025.
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
Artifact (private, claude.ai): https://claude.ai/artifact/WB1nNKgdRTwnA2GVmXNK6h (v3, 778 entries). Republish: Artifact publish with `url`, `file_path` = index.html, `files` = every `flags/*.svg` mapped to itself.

## Data status (778 entries built: fb 652, bb 126)
All files in `data/` pass `validate.py`. `build.py` only ships EuroLeague (`cat: euro`) matches from 2019–2025 (`YEARS` in build.py); the 29 older entries stay in b02_euro.json but are skipped.
| file | scope | n | how verified |
|---|---|---|---|
| b01_nba.json | NBA starting fives 2012–2025 | 55 | box scores |
| b02_euro.json | EuroLeague 2012–2025 (no Serbian clubs); only 2019–2025 built (21) | 50 | box scores |
| b03_srb.json | Serbia basketball NT + opponents + Zvezda/Partizan/Mega | 50 | box scores |
| f01_ucl.json | Champions League 2009/10–2024/25, finals + legendary nights | 60 | web |
| f02_uel.json | Europa/Conference League finals, UEFA Super Cup, Club World Cup, famous EL nights | 64 | 55 from the local session (web), plus 9 Super Cup / Club World Cup finals (7 Transfermarkt, 2 from memory: Real Madrid Super Cups 2022, 2024) |
| f03_eng_big.json | Big six, domestic only (~9 per club) | 55 | 47 Transfermarkt, 5 StatsBomb, 4 web |
| f04_partial.json | English non-big-six clubs | 55 | web |
| f04_eng_cult.json | English non-big-six clubs, extra team+seasons not in f04_partial | 7 | Transfermarkt |
| f05_esp.json | Spanish clubs, domestic only | 55 | 32 StatsBomb, 22 Transfermarkt, 1 web |
| f06_ita.json | Italian clubs, domestic only | 74 | 55 from the local session (web), plus 19 extra team+seasons (web / Transfermarkt) |
| f07_ger_fra.json | German + French clubs, domestic only | 55 | 10 web, 45 StatsBomb (many are ordinary league games: Leverkusen 15/16 & 23/24 opponents, Ligue 1 15/16, PSG 21/22–22/23 opponents) |
| f08_rest.json | Clubs outside ENG/ESP/ITA/GER/FRA/SRB, domestic/non-UEFA | 60 | 11 web (Libertadores finals), 49 Transfermarkt |
| f09_wc.json | World Cups 2010–2022 + famous qualifiers (no Serbia) | 60 | web |
| f10_euro_copa.json | Euros, Copa América, AFCON, Nations League, Asian Cup, Gold Cup, Olympics (no Serbia) | 60 | web |
| f11_srb_clubs.json | Crvena zvezda 11, Partizan 9, Vojvodina 5 (target was 45) | 25 | 7 web, 18 Transfermarkt |
| f12_srb_nat.json | Serbia football NT (+U20 2015, U19 2013) | 22 | web |

Still thin: f11_srb_clubs.json (25/45). The Transfermarkt dataset has no Serbian lineups before 2012/13, no Kup Srbije, and Superliga only from 2024/25, so Partizan CL 2010/11, cup finals and older derbies need web verification.

Verification sources that worked from a cloud session where Wikipedia/ESPN/worldfootball/flagcdn were blocked and the WebSearch budget (200 calls per session, shared by all agents) ran out:
- Transfermarkt dataset (lineups 2012/13+, per-match positions and formation): `https://media.githubusercontent.com/media/thivvu-glitch/BINA_Projekt/HEAD/Data/{game_lineups,games,players,clubs}.csv`
- StatsBomb open data (exact positions): `https://raw.githubusercontent.com/statsbomb/open-data/master/data/...`
- Flags: when flagcdn.com is unreachable, copy `flags/4x3/<cc>.svg` from the `flag-icons` npm package (`npm pack flag-icons`).

## Game rules implemented
- Per player: Wordle grid, length = letters of the known name (diacritics stripped, đ→DJ, spaces/hyphens removed), 6 tries (4 in "Teško", which also hides flags).
- Name length is shown as dashes (one per letter) on each shirt and in the guess panel; on phones the shirt shows only dashes, the try counter stays in the panel.
- Duplicate surnames in one lineup are allowed (both shirts accept the same answer).
- Random deck without repeats per sport/category (localStorage), "Dnevna" = daily puzzle seeded by date, stats, share text.

## Possible next steps
- Extend f11_srb_clubs.json toward 45 (needs web access for pre-2012 and domestic cup matches).
- EuroLeague 2019–2025 has only 21 built entries; add more verified 2019–2025 games to b02_euro.json.
- Spot-check left/right order in a few lineups (agents flagged formation/side doubts, never player identity).
- Optional: GitHub Pages (make repo public, add full `<head>` wrapper as `index.html`).
