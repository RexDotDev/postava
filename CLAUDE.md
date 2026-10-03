# postava
"Squads" (repo `postava`, Serbian for "lineup"): a static Wordle-style game where you guess the real starting XI (football) or five (basketball) of famous matches, letter by letter. Aimed at advanced fans (SPEC audience: Serbia); UI and all data text are in English. Live: https://www.guessthesquad.com

## Stack
- One self-contained `src.html` (vanilla HTML/CSS/JS, no framework, no npm, no bundler; Google Fonts via CDN only). Sound effects are synthesised with Web Audio (no audio files).
- Python 3 stdlib-only scripts. Local `python3` is 3.9.6 (CI: ubuntu-latest), so no 3.10+ syntax. No tests, no linter; the only automated check is `.github/workflows/check.yml`.
- Optional tools: `tools/gen_euroleague.py` (needs `pycountry`; `--write` appends to `data/b02_euro.json`), `tools/make_images.mjs` (Playwright; renders `og.png` and icons).

## Commands
- `python3 validate.py data/<file>.json` checks ONE file (arg required); prints `OK <n> entries`, exit 1 on errors. Run on every file you touch.
- `python3 build.py` merges all `data/*.json` and rewrites TRACKED `index.html` and `data.<hash>.json` (old hashed file deleted), plus new `flags/*.svg` if a country lacks one, plus gitignored `artifact.html`. Prints `built N entries (fb X, bb Y), dropped D, outside year window S, flags F` and `DROP <file> <team> <season> <errors|dup>` per rejected entry. Now: 702 built of 731 raw.
- `build.py` has no flags and no `--help`: its only arg is a glob of data files, and any non-matching or partial glob overwrites the site with a partial or EMPTY one (`--help` wipes it to 0 entries). Never pass an arg you will commit.
- Preview: `python3 build.py && python3 -m http.server 8000`.

## Structure
- `src.html` the game (UI + logic). Build injects data at `const DATA = /*DATA*/[];` (build asserts the script starts with exactly `<script>\nconst DATA = /*DATA*/[];`); the site build swaps it for a module that fetches `data.<hash>.json`.
- `data/*.json` 15 files, one scope each (counts at d9ae840): basketball `b01_nba` 55, `b02_euro` 96, `b04_nat_legends` 43, `b05_nat_recent` 48 (no b03); football `f01_ucl` 57, `f02_uel` 56, `f03_eng_big` 55, `f04_partial` 21, `f04_eng_cult` 2, `f05_esp` 44, `f06_ita` 60, `f07_ger_fra` 34, `f08_rest` 40, `f09_wc` 60, `f10_euro_copa` 60 (no f11/f12).
- `index.html` + `data.<hash>.json` build output, committed and served as-is; never hand-edit. index.html is a full page (head, OG tags from `SITE_URL`).
- `flags/<cc>.svg` 112 flags, referenced as relative `flags/xx.svg`. `icon.svg`, `apple-touch-icon.png`, `icon-512.png`, `og.png`, `site.webmanifest` site assets.
- Docs: `SPEC.md` data schema and quality rules (read fully before writing data), `MAINTAINING.md` deploy, per-file scope/verification table, sources, `CONTRIBUTING.md`, `README.md`. No HANDOFF.md any more.
- `vercel.json` cache headers, `.vercelignore` (only the built site is served), `.nojekyll`, `.github/` (check workflow, `rulesets/protect-main.json`, issue forms, CODEOWNERS).

## Data schema
- Entry: sport `fb|bb`, cat (fb `club|nat`; bb `nba|euro|nat`), team, opp, score (team's score first), comp, season, y (int), form, kit, okit, p, optional note (<= 90 chars, must not contain a lineup player's short name; validate checks). kit/okit = `[pattern, "#rrggbb", "#rrggbb"]`, pattern from the list in SPEC.
- Player = `[short, full, cc]`. short = what a fan types (usually surname). cc = lowercase ISO alpha-2, `gb-eng|gb-sct|gb-wls|gb-nir`, `xk` for Kosovo, never `gb` (validate would NOT catch it: any 2 letters pass the regex).
- ORDER drives pitch placement. Football: 11 players, GK, then each line defence to attack, each line left to right; `form` numbers sum to 10. Basketball: `form` is `"5"`, 5 players PG, SG, SF, PF, C.
- Year windows (validate): fb >= 2009, bb nba/euro >= 2012, bb nat >= 1970 (data starts 1989), max 2026. build also keeps EuroLeague only 2019-2025 (`YEARS` in build.py), so 29 older `b02_euro` entries are skipped.
- Dedupe: build drops by (sport, team, season, comp) across files, sorted filename order wins. validate also rejects duplicate (team, season) within one file. App entry id = `sport|team|season|comp`.
- `norm()` in src.html and `key()` in validate.py must stay in sync (đ becomes DJ, ø/æ/ß/ł/ı/ð/þ table, NFD, keep A-Z only; spaces, hyphens, apostrophes vanish). Known drift: key() lacks upper-case Æ; validate allows 3-18 letters while SPEC says 3-16.

## Conventions
- One entry = one real match with real opponent, score and actual starting lineup. Accuracy is the product: every lineup change needs a source (PR template), stay inside the file's scope, no matches after July 2025 unless verified.
- Commit a data change together with the rebuilt `index.html`, `data.<hash>.json` and new flags, or CI fails. Short imperative commit subjects; changes reach `main` through pull requests.
- Game: 6 tries per player (Hard: 4 tries, flags hidden); Daily = `all[hash(sport+day) % all.length]` over every entry of the sport, ignoring the category filter; random deck without repeats; state in localStorage `postava:v1`.

## Deploy
- Vercel project `postava` (team reljas-projects) is connected to github.com/RexDotDev/postava. Every merge/push to `main` redeploys https://www.guessthesquad.com (apex redirects to www); PRs get previews. No build step on Vercel: it serves the committed files.
- `main` ruleset: PR required, check `validate-and-build` must pass (validate each data file, then `python3 build.py` must leave `git status --porcelain` empty).
- `SITE_URL` (env var or constant in build.py) sets absolute og:image/canonical URLs. A private claude.ai Artifact copy (publish `artifact.html` + `flags/*.svg`) is described in MAINTAINING.md; it is not the live site.

## Gotchas
- `build.py` `exec`s the part of `validate.py` before the text `data = json.load`; keep that line, and keep everything above it definitions-only.
- Output is sorted by (sport, y, team): adding or removing any entry shifts entry numbers `#n` and the daily puzzle. Saved progress is keyed by entry id; changing an entry's team, season or comp orphans it.
- The data file name is sha1[:10] of its content, so every data change renames it; the build deletes the old `data.*.json` (shows as a delete + add in git).
- build strips leading initials from short names ("V. Milinković-Savić" becomes "Milinković-Savić"); it downloads missing flags from flagcdn.com (needs network; fallback in MAINTAINING.md).
- The Serbia category and lesser-known clubs were removed on purpose (commit 5f59da6); `gen_euroleague.py` still skips Serbian clubs. Open todo: spot-check left/right order in a few lineups.
