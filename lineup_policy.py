"""Selection rules for the playable pool; source files retain historical matches."""
import re

MIN_EUROLEAGUE_SEASON = 2020


def exclusion_reason(entry):
    if (entry.get("sport"), entry.get("cat")) == ("bb", "euro"):
        season = re.match(r"^(\d{4})/\d{2,4}$", entry.get("season", ""))
        if not season or int(season.group(1)) < MIN_EUROLEAGUE_SEASON:
            return "EuroLeague before 2020/21"
    comp = entry.get("comp", "")
    if re.search(r"friendly|exhibition|pre[ -]?season|testimonial", comp, re.I):
        return "friendly or exhibition"
    return None
