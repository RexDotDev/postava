"""Selection rules for the playable pool; source files retain historical matches."""
import re

MIN_EUROLEAGUE_SEASON = 2020

# Familiar European and South American national teams. An exceptional tournament
# does not make every lineup of a smaller national team suitable for the game.
FOOTBALL_NATIONS = {
    "Argentina", "Belgium", "Brazil", "Chile", "Colombia", "Croatia", "Denmark",
    "England", "France", "Germany", "Italy", "Netherlands", "Portugal",
    "Spain", "Switzerland", "Turkey", "Uruguay",
}
ICONIC_NATIONAL_MATCHES = {
    ("Iceland", "2016", "Euro 2016, round of 16", "England"),
    ("Wales", "2016", "Euro 2016, quarter-final", "Belgium"),
    ("Morocco", "2022", "World Cup 2022, quarter-final", "Portugal"),
}


def exclusion_reason(entry):
    if (entry.get("sport"), entry.get("cat")) == ("bb", "euro"):
        season = re.match(r"^(\d{4})/\d{2,4}$", entry.get("season", ""))
        if not season or int(season.group(1)) < MIN_EUROLEAGUE_SEASON:
            return "EuroLeague before 2020/21"
    comp = entry.get("comp", "")
    if re.search(r"friendly|exhibition|pre[ -]?season|testimonial", comp, re.I):
        return "friendly or exhibition"
    if (entry.get("sport"), entry.get("cat")) == ("fb", "nat"):
        match = tuple(entry.get(k) for k in ("team", "season", "comp", "opp"))
        if entry.get("team") not in FOOTBALL_NATIONS and match not in ICONIC_NATIONAL_MATCHES:
            return "outside European/South American national selection"
    return None
