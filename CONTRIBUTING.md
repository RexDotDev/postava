# Contributing

Thanks for helping. Most contributions are lineup fixes and new matches, and a wrong player ruins a puzzle, so every data change needs a source.

## Report a wrong lineup

Open an issue with the **Wrong lineup** form: the match, what is wrong, and a link to a match report or box score that shows the correct lineup.

## Add or fix lineups

1. Read [SPEC.md](SPEC.md). Each match is one JSON object: teams, score, competition, season, formation, kits and the eleven (or five) starters in pitch order.
2. Edit the right file in `data/` and run `python3 validate.py <file>` until it prints `OK`.
3. Run `python3 build.py`, open the puzzle locally (`python3 -m http.server 8000`) and check it.
4. Commit the data file together with the rebuilt `index.html`, `data.<hash>.json` and any new `flags/*.svg`.
5. Open a pull request and link a source for every match you added or changed.

## Code changes

The game is one file, `src.html`, with no framework or build dependencies beyond Python 3, and it should stay that way. For anything bigger than a fix, open an issue first so we can agree on the approach. Check changes on a phone-sized screen as well as a desktop one.

## Checks

Every pull request runs `.github/workflows/check.yml`: it validates each file in `data/` and rebuilds the site. It fails if `validate.py` reports an error or if the committed `index.html` and `data.<hash>.json` do not match a fresh build. Pull requests are merged into `main` once the check passes, and every merge redeploys the site.

By contributing you agree that your contribution is released under the [MIT License](LICENSE).
