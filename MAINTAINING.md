# Maintaining Squads

Notes for whoever works on the game and its data next. The README covers what the game is and how to run it.
UI and all data text (comp, note, team names) are in English. The repository is named `postava`, Serbian for "lineup".

## Files
- `src.html` — the whole game (UI + logic). Data is injected at `/*DATA*/[]`.
- `build.py` — merges `data/*.json`, validates, drops bad/dup entries, strips leading initials ("V. Milinković-Savić" → "Milinković-Savić"), fetches missing flags (flagcdn.com) into `flags/`, writes `index.html`, `data.<hash>.json` and `artifact.html`.
- `validate.py <file>` — schema check (run on every data file; exits 1 on errors).
- `SPEC.md` — data schema + quality rules. Read it before adding lineups.
- `index.html` + `data.<hash>.json` — built standalone site for static hosting: GitHub Pages (branch `main`, folder `/`) or Vercel (framework "Other", no build command, output `.`). The page loads the lineups from the content-hashed JSON (new name on every data change, so it can be cached forever; `vercel.json` sets the cache headers, `.vercelignore` keeps sources off the site, `.nojekyll` stops Jekyll on Pages).
- `icon.svg`, `apple-touch-icon.png`, `icon-512.png`, `og.png` (1200×630 link preview), `site.webmanifest` — site icons and share image. Regenerate the PNGs with `node tools/make_images.mjs` (Playwright) from `icon.svg` and `tools/og.html`.
- `SITE_URL` in `build.py` (or the `SITE_URL` env var) — public address of the site, currently `https://www.guessthesquad.com` (Vercel project `postava`, team reljas-projects). Change it with a custom domain and rebuild: link previews need an absolute `og:image` URL.
- `artifact.html` — the same page with the data inlined and without `<html>/<head>`, for the claude.ai Artifact (the publisher adds them). Built locally, not committed.
- `flags/<cc>.svg` — nationality flags referenced as relative `flags/xx.svg`.

Build: `python3 build.py` → prints `built N entries (fb X, bb Y)`.

## Deployment
- Site: https://www.guessthesquad.com (apex `guessthesquad.com` redirects to www; the domain was bought through Vercel; `postava-beta.vercel.app` still serves the same deployment) — Vercel project `postava` (team reljas-projects), connected to this repository. Every push to `main` redeploys; pull requests get preview deployments. No build step: Vercel serves the committed `index.html`, `data.<hash>.json`, `flags/` and icons.
- GitHub: `.github/workflows/check.yml` runs on every pull request and push to `main` (job `validate-and-build`: `validate.py` on each data file, then `build.py` must leave no changes). `.github/rulesets/protect-main.json` is the ruleset for `main` (pull request required, check `validate-and-build` required, no force pushes or deletion); import it under Settings → Rules → Rulesets. Dependabot keeps the workflow actions up to date.
- claude.ai Artifact (private): https://claude.ai/artifact/WB1nNKgdRTwnA2GVmXNK6h. Republish: Artifact publish with `url`, `file_path` = artifact.html, `files` = every `flags/*.svg` mapped to itself.

## Data status (887 entries built: fb 633, bb 254)
All 933 source entries in `data/` pass `validate.py`. `lineup_policy.py` excludes only 46 historical EuroLeague entries before 2020/21; 29 were already outside the earlier playable window and 17 were newly excluded. The 58 football national-team entries from the initial revision are restored. Friendlies are automatically excluded in every category.

The 2020/21 cutoff applies **only to EuroLeague**, based on season start rather than `y`. Football and basketball national teams retain their original historical ranges. NBA's minimum match year is now 2011 so the 2010/11 Mavericks, Heat, Bulls, Lakers and Celtics can be played. Both Random and Daily use the same selection.

The expansion adds 202 distinct starting lineups: 106 football clubs, 38 football national teams, 36 NBA, 20 EuroLeague and 2 basketball national teams. It includes 18 lineups from 2026, with 2026/27 club seasons represented in football, NBA and EuroLeague. `DATA_ADDITIONS.md` lists every added puzzle. Each new source entry stores verification date, match date and source URLs. StatsBomb/Hudl entries use the actual Starting XI event (formation + positions) and lineup metadata (country and nickname), NBA feed snapshots use nonempty START_POSITION, and EuroLeague snapshots use IsStarter. Exact team+starting-XI duplicates were excluded even when the match differed.

The table below describes the original source archive; expansion files follow it.

| file | scope | n | how verified |
|---|---|---|---|
| b01_nba.json | NBA starting fives 2012–2025 | 55 | box scores |
| b02_euro.json | EuroLeague 2012–2025 (no Serbian clubs); only 2020/21–2024/25 built (50) | 96 | box scores; the 49 added 2019–2025 games come straight from the official EuroLeague feed (`tools/gen_euroleague.py`: starters, positions, nationality) |
| b04_nat_legends.json | Basketball national teams, legendary games 1989–2025: Dream Team 1992, USA gold medals, Yugoslavia's 1989–2002 finals, Spain, Argentina, Greece, Lithuania, France, Germany; plus the Serbia, USA, Slovenia and Germany finals of 2014–2023 | 43 | official Olympic reports and FIBA box scores (starter flags), Wikipedia box scores, transcribed FIBA box scores (piratasdelbasket.net) for the 1989–2003 games; two sources agree or the game was dropped |
| b05_nat_recent.json | Basketball national teams 2008–2025: Olympics, World Cups and EuroBasket finals, semi-finals, bronze games, quarter-finals and upsets | 48 | official FIBA game pages (per-player starter flag), official Olympic reports, ESPN and Basketball-Reference box scores |
| f01_ucl.json | Champions League 2009/10–2024/25, finals + legendary nights | 57 | web |
| f02_uel.json | Europa/Conference League finals, UEFA Super Cup, Club World Cup, famous EL nights | 56 | 55 from the local session (web), plus 9 Super Cup / Club World Cup finals (7 Transfermarkt, 2 from memory: Real Madrid Super Cups 2022, 2024) |
| f03_eng_big.json | Big six, domestic only (~9 per club) | 55 | 47 Transfermarkt, 5 StatsBomb, 4 web |
| f04_partial.json | English clubs outside the big six (Everton, Aston Villa, Newcastle, West Ham, Leicester, Leeds, Southampton) | 21 | web |
| f04_eng_cult.json | Same clubs, extra team+seasons not in f04_partial | 2 | Transfermarkt |
| f05_esp.json | Spanish clubs, domestic only | 44 | 32 StatsBomb, 22 Transfermarkt, 1 web |
| f06_ita.json | Italian clubs, domestic only | 60 | 55 from the local session (web), plus 19 extra team+seasons (web / Transfermarkt) |
| f07_ger_fra.json | German + French clubs, domestic only | 34 | 10 web, 45 StatsBomb (many are ordinary league games: Leverkusen 15/16 & 23/24 opponents, Ligue 1 15/16, PSG 21/22–22/23 opponents) |
| f08_rest.json | Clubs outside ENG/ESP/ITA/GER/FRA (Dutch, Portuguese, Scottish, Turkish, Ukrainian, South American and a few others), domestic/non-UEFA | 40 | 11 web (Libertadores finals), 49 Transfermarkt |
| f09_wc.json | World Cups 2010–2022 + famous qualifiers | 60 | web |
| f10_euro_copa.json | Euros, Copa América, AFCON, Nations League, Asian Cup, Gold Cup, Olympics | 60 | web |

Expansion files:

| Files | New entries | Verification |
|---|---:|---|
| f11_expansion_club.json | 10 | UEFA official reports and lineups, Sky Sports, official Bayern report and LFChistory |
| f12_expansion_nat.json | 4 | World Cup 2026 team sheets and match reports |
| f13_verified_01–03.json | 130 | StatsBomb Open Data, provided by Hudl: actual Starting XI event, lineup metadata and match results |
| b06_expansion_nba.json | 12 | RealGM starter flags; official NBA results where relevant |
| b07_expansion_euro.json | 4 | November 2026 box scores with explicit starter markers |
| b08_expansion_nat.json | 2 | FIBA results and Global Sports Archive starter flags, August 2026 |
| b09_verified_nba.json | 24 | NBA feed snapshots in statsbase/statsbase: START_POSITION, player info and game logs; starter count and team score reconciled |
| b10_verified_euro_01–02.json | 16 | Official EuroLeague feed snapshots in bsamot10/EuroleagueDataETL: IsStarter and quarter scores |

Removed on purpose: the Serbia category (clubs and national teams), and the lineups of lesser-known clubs (Greek, Russian and Saudi clubs, most English, Spanish, Italian, German and French sides outside the big names). They are in the git history (commit "Remove the Serbia category and lesser-known clubs") if you want any back.

Legend games we could not confirm are not in the data: the 1990 World Championship final (Yugoslavia), USSR 1972 and 1988, Lithuania 1992 and 1996, Croatia 1992 final, Italy 2004, Greece 2006, France 2000, USA 1984 and 1988, Yugoslavia 1980 and 1988. Add them only with a box score that marks the starters.

Verification sources that work without scraping match-report sites:
- Transfermarkt dataset (lineups 2012/13+, per-match positions and formation): `https://media.githubusercontent.com/media/thivvu-glitch/BINA_Projekt/HEAD/Data/{game_lineups,games,players,clubs}.csv`
- StatsBomb open data (exact positions): `https://raw.githubusercontent.com/hudl/open-data/master/data/...`
- Flags: when flagcdn.com is unreachable, copy `flags/4x3/<cc>.svg` from the `flag-icons` npm package (`npm pack flag-icons`).

## Game rules implemented
- Per player: Wordle grid, length = letters of the known name (diacritics stripped, đ→DJ, spaces/hyphens removed), 6 tries (4 in Hard mode, which also hides flags).
- Name length is shown as dashes (one per letter) on each shirt and in the guess panel; on phones the shirt shows only dashes, the try counter stays in the panel.
- Duplicate surnames in one lineup are allowed (both shirts accept the same answer).
- One letter hint per lineup, shared across all players, available in Normal and Hard. It picks an unknown position, costs no try, persists in the saved game and is marked in share text. Older saves without `hint` remain compatible. Reopening the current Daily resumes its hint and guesses.
- Random deck without repeats per sport/category (localStorage), Daily = puzzle seeded by the date, stats, share text.
- The accent colour (selected player, active filter, focus ring) follows the kit of the team on screen (`teamAccent` in `src.html`).

## Regression checks

Run `python3 -m unittest discover -s tests` and `node --test tests/hint.test.cjs` (Node.js 22+, no npm dependencies). These check the EuroLeague-only cutoff, restored national teams, friendly exclusions, the 200+ expansion and per-entry provenance, distinct XIs, shipped-data coverage, hint limits, persistence, old saves and Daily resume. CI runs them before checking a fresh build. Browser layout still needs a desktop and phone spot check.

## Possible next steps
- Basketball national teams: the FIBA game pages (`fiba.basketball/en/history/...` and `/en/events/.../games/...`) carry a per-player starter flag in the page data, which makes 2009+ games easy to verify. Do not use API keys taken from page source.
- More EuroLeague games: `python3 tools/gen_euroleague.py --write` (raise PER_SEASON). Check nationality: the feed reports passports, so naturalized national-team players need CC_OVERRIDE.
- Spot-check left/right order in a few lineups (formation and side are sometimes inferred; player identity is not).
