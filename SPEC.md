# SQUADS — lineup data spec (read fully before writing)

Game: players see a real match (team, opponent, score, competition) and a pitch/court with the
team's starting players as shirts (nationality flag only). They guess each player's name Wordle-style
(letter count shown). Audience: ADVANCED football/basketball fans from Serbia. Accuracy is everything —
a wrong player in a lineup ruins the puzzle.

## Output
Write ONE UTF-8 JSON file (an array of objects) to the path given in your task. Then run:
    python3 validate.py <your file>
and fix everything it reports until it prints OK.

## Object schema
{
  "sport": "fb",                 // "fb" football | "bb" basketball
  "cat": "club",                 // fb: "club" | "nat" | "srb"   bb: "nba" | "euro" | "srb"
                                 //   "srb" = Serbian clubs (Red Star Belgrade, Partizan, Vojvodina, Mega...) AND Serbian national teams
  "team": "Leicester City",      // team whose starting lineup is the puzzle (English name: "Serbia", "Red Star Belgrade", "USA")
  "opp": "Manchester City",      // opponent
  "score": "3-1",                // TEAM's score first. Pens/ET/OT: "1-1 (4-3 pen.)", "2-1 a.e.t.", basketball "95-88" / "101-98 OT"
  "comp": "Premier League, matchday 25",   // English, short: "Champions League final", "World Cup 2014, semi-final",
                                           // "EuroLeague Final Four, final", "NBA Finals, Game 7", "Serbian Cup final"
  "season": "2015/16",           // club season "2015/16", or tournament year "2014"
  "y": 2016,                     // calendar year of the match (int)
  "note": "Season of miracles: title at 5000-1 odds",   // optional, English, <= 90 chars, shown AFTER the game.
                                                    // NEVER mention any player of this lineup in the note.
  "form": "4-4-2",               // football: outfield lines defence→attack, must sum to 10 ("4-2-3-1", "3-4-2-1", "4-1-4-1", "5-3-2"...)
                                 // basketball: always "5"
  "kit":  ["stripes", "#e30613", "#ffffff"],   // team shirt doodle for THAT season: [pattern, main hex, secondary hex]
  "okit": ["solid", "#6cabdd", "#ffffff"],     // opponent shirt, same format
  "p": [ ["Schmeichel", "Kasper Schmeichel", "dk"], ... ]
}

Kit patterns: solid (c2 = collar/trim) | stripes (vertical c1/c2, e.g. Juventus, Zvezda, Partizan, Barça) |
hoops (horizontal, Celtic) | halves (left c1 / right c2) | sash (diagonal c2 band on c1, River, Peru, Vasco) |
sleeves (c1 body, c2 sleeves, Arsenal) | pinstripes (thin c2 lines on c1) | quarters | checks (Croatia) |
chevron (V on chest) | band (horizontal chest band). Use the kit the team actually wore in that match if known,
otherwise their home kit of that season. Use real club/national colours (Zvezda red/white stripes, Partizan black/white stripes,
Vojvodina red/white, Valencia white with black/orange trim, etc.).

## Players array "p"
Each player = [short, full, cc]
- short: the name a fan would TYPE — the name on the shirt / how the player is universally known.
  Usually the surname ("Vardy", "Van Dijk", "De Bruyne", "Kanté", "Mitrović", "Alexander-Arnold").
  Mononyms where the player is known by one name ("Xavi", "Pedro", "Neymar", "Marcelo", "Casemiro", "Isco", "Koke",
  "Fabinho", "Pepe", "Rodri", "Jorginho", "Hulk"). "Cristiano Ronaldo" → "Ronaldo". Keep diacritics (the game strips them;
  đ becomes DJ). After stripping spaces/hyphens/apostrophes it must be 3–16 letters.
- full: full common name with diacritics ("Kasper Schmeichel", "Dušan Tadić").
- cc: nationality (the national team the player represents; else birth country), lowercase ISO 3166-1 alpha-2
  ("rs", "hr", "ba", "me", "mk", "si", "br", "ar"...). UK: "gb-eng", "gb-sct", "gb-wls", "gb-nir". Kosovo: "xk".
  Ireland "ie". Never "gb" or "uk".

ORDER (critical, it drives pitch placement):
- Football: GK first. Then each formation line from defence to attack. WITHIN a line list players LEFT → RIGHT
  as seen with the team attacking upward: left-back first … right-back last; left winger first … right winger last.
  Example 4-3-3: GK, LB, LCB, RCB, RB, LCM, CM, RCM, LW, ST, RW.
  4-2-3-1: GK, LB, LCB, RCB, RB, LDM, RDM, LAM(LW), CAM, RAM(RW), ST.
- Basketball: exactly 5 starters, order PG, SG, SF, PF, C.

## Quality rules
1. Every entry is ONE REAL MATCH with the real opponent and real final score, and "p" is that match's actual
   STARTING lineup (not subs, not "best XI"). Formation = the shape actually used.
2. Pick famous matches: finals, title deciders, legendary wins/upsets, derbies, big European nights, tournament games.
   For an iconic season-team (e.g. Leicester 2015/16), pick one well-documented match where the classic XI started.
3. Only include lineups you are highly confident about. Use WebSearch to verify any lineup you are not 100% sure of
   (always for less famous matches and for Serbian/regional clubs). Do not guess. If you cannot verify, pick a different match.
4. At most one entry per team per season in your file. The same club in different seasons is great.
5. Mix: ~60% instantly recognisable iconic teams, ~40% deeper cuts that a serious fan still knows.
6. Stay strictly inside your assigned scope (other agents cover other scopes; overlap creates duplicates).
7. Dates are from the 2009 calendar year onward for football, 2012 onward for basketball. Do not include matches
   from after July 2025 unless you verified them with WebSearch.
