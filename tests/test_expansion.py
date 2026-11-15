import datetime
import glob
import json
from pathlib import Path
import unittest
import unicodedata
import re


def key(name):
    name = name.replace("đ", "dj").replace("Đ", "Dj").replace("ł", "l").replace("Ł", "L")
    return re.sub("[^A-Z]", "", unicodedata.normalize("NFD", name).upper())


class ExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = []
        for path in glob.glob("data/*.json"):
            with open(path, encoding="utf-8") as source:
                cls.all.extend(json.load(source))
        cls.new = [e for e in cls.all if e.get("verified") == "2026-11-15"]

    def test_at_least_200_new_lineups_with_all_categories_and_current_matches(self):
        self.assertGreaterEqual(len(self.new), 200)
        expected = {("fb", "club"), ("fb", "nat"), ("bb", "nba"), ("bb", "euro"), ("bb", "nat")}
        self.assertEqual({(e["sport"], e["cat"]) for e in self.new}, expected)
        self.assertEqual({(e["sport"], e["cat"]) for e in self.new if e["y"] == 2026}, expected)
        for cat in ("nba", "euro"):
            self.assertTrue(any(e["cat"] == cat and e["season"] == "2026/27" for e in self.new))

    def test_sources_dates_and_flags_are_present(self):
        for e in self.new:
            self.assertTrue(e.get("sources"), e)
            self.assertTrue(all(s.startswith("https://") for s in e["sources"]))
            date = datetime.date.fromisoformat(e["date"])
            self.assertLessEqual(date, datetime.date.fromisoformat(e["verified"]))
            self.assertEqual(date.year, e["y"])
            for player in e["p"]:
                self.assertTrue(Path("flags", player[2] + ".svg").exists(), player)

    def test_no_duplicate_entry_or_duplicate_starting_lineup(self):
        ids = set()
        old_squads = {(e["sport"], e["team"], frozenset(key(p[1]) for p in e["p"]))
                      for e in self.all if e not in self.new}
        for e in self.all:
            identity = tuple(e[k] for k in ("sport", "team", "season", "comp"))
            self.assertNotIn(identity, ids)
            ids.add(identity)
        for e in self.new:
            squad = (e["sport"], e["team"], frozenset(key(p[1]) for p in e["p"]))
            self.assertNotIn(squad, old_squads, e)
            old_squads.add(squad)

    def test_shipped_pool_includes_every_new_entry(self):
        with open(glob.glob("data.*.json")[0], encoding="utf-8") as source:
            shipped = json.load(source)
        ids = {tuple(e[k] for k in ("sport", "team", "season", "comp")) for e in shipped}
        for e in self.new:
            self.assertIn(tuple(e[k] for k in ("sport", "team", "season", "comp")), ids)


if __name__ == "__main__":
    unittest.main()
