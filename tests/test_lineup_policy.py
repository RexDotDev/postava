import glob
import json
import unittest

from lineup_policy import exclusion_reason


class LineupPolicyTests(unittest.TestCase):
    def entry(self):
        return dict(sport="fb", cat="club", team="Chelsea", opp="Manchester City",
                    season="2020/21", y=2021, comp="Champions League final")

    def test_euroleague_boundary_uses_season_not_calendar_year(self):
        old = self.entry()
        old.update(sport="bb", cat="euro", season="2019/20", y=2020)
        self.assertIsNotNone(exclusion_reason(old))
        old.update(season="2020/21", y=2021)
        self.assertIsNone(exclusion_reason(old))

    def test_cutoff_does_not_apply_to_football_nba_or_basketball_nations(self):
        for sport, cat, team, season, comp in [
            ("fb", "club", "Barcelona", "2008/09", "Champions League final"),
            ("fb", "nat", "Spain", "2010", "World Cup 2010, final"),
            ("bb", "nba", "Miami Heat", "2011/12", "NBA Finals, Game 5"),
            ("bb", "nat", "USA", "1992", "Olympics 1992, final"),
        ]:
            entry = self.entry()
            entry.update(sport=sport, cat=cat, team=team, season=season, comp=comp)
            self.assertIsNone(exclusion_reason(entry), entry)

    def test_delayed_euro_and_olympics_remain_playable(self):
        euro = self.entry()
        euro.update(cat="nat", team="Italy", season="2020", y=2021, comp="Euro 2020, final")
        self.assertIsNone(exclusion_reason(euro))
        euro.update(sport="bb", team="USA", comp="Olympics 2020, final")
        self.assertIsNone(exclusion_reason(euro))

    def test_friendlies_are_excluded_in_every_category(self):
        for sport, cat in [("fb", "club"), ("fb", "nat"), ("bb", "nba"), ("bb", "euro"), ("bb", "nat")]:
            for comp in ["International friendly", "Pre-season tournament", "Exhibition game", "Testimonial"]:
                entry = self.entry()
                entry.update(sport=sport, cat=cat, comp=comp)
                self.assertIsNotNone(exclusion_reason(entry))

    def test_national_teams_follow_curated_european_and_south_american_selection(self):
        for team in ("France", "England", "Spain", "Croatia", "Argentina", "Brazil", "Chile", "Uruguay"):
            entry = self.entry()
            entry.update(cat="nat", team=team, season="2022", comp="World Cup 2022, quarter-final")
            self.assertIsNone(exclusion_reason(entry), entry)
        for team in ("Zambia", "Cape Verde", "Qatar", "Jordan", "Canada", "Japan", "Albania", "Venezuela"):
            entry = self.entry()
            entry.update(cat="nat", team=team, season="2022", comp="World Cup 2022, quarter-final")
            self.assertIsNotNone(exclusion_reason(entry), entry)

    def test_legendary_exceptions_are_exact_matches(self):
        for team, season, comp, opp in [
            ("Morocco", "2022", "World Cup 2022, quarter-final", "Portugal"),
            ("Iceland", "2016", "Euro 2016, round of 16", "England"),
            ("Wales", "2016", "Euro 2016, quarter-final", "Belgium"),
        ]:
            entry = self.entry()
            entry.update(cat="nat", team=team, season=season, comp=comp, opp=opp)
            self.assertIsNone(exclusion_reason(entry), entry)
            entry.update(season="2025", comp="AFCON 2025, quarter-final")
            self.assertIsNotNone(exclusion_reason(entry), entry)

    def test_zambia_cannot_appear_in_random_or_daily_data(self):
        with open(glob.glob("data.*.json")[0], encoding="utf-8") as source:
            shipped = json.load(source)
        self.assertFalse(any(e["sport"] == "fb" and e["team"] == "Zambia" for e in shipped))

    def test_shipped_pool_obeys_policy_and_contains_both_sports(self):
        paths = glob.glob("data.*.json")
        self.assertEqual(len(paths), 1)
        with open(paths[0], encoding="utf-8") as source:
            entries = json.load(source)
        self.assertEqual({e["sport"] for e in entries}, {"fb", "bb"})
        for entry in entries:
            self.assertIsNone(exclusion_reason(entry), entry)
        self.assertTrue(any(e["team"] == "Morocco" and e["season"] == "2022" for e in entries))
        for sport, cat, team, season in [
            ("fb", "club", "Barcelona", "2008/09"),
            ("fb", "nat", "Spain", "2010"),
            ("bb", "nba", "Miami Heat", "2011/12"),
            ("bb", "nat", "USA", "1992"),
        ]:
            self.assertTrue(any((e["sport"], e["cat"], e["team"], e["season"])
                                == (sport, cat, team, season) for e in entries))


if __name__ == "__main__":
    unittest.main()
