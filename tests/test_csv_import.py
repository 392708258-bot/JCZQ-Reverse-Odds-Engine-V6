import csv
import os
import tempfile
import unittest

from main import load_match_from_csv


class CsvImportTest(unittest.TestCase):
    def test_load_match_from_csv(self):
        with tempfile.NamedTemporaryFile("w", newline="", suffix=".csv", delete=False) as handle:
            writer = csv.writer(handle)
            writer.writerow([
                "match_id",
                "home_team",
                "away_team",
                "win_odds",
                "draw_odds",
                "lose_odds",
                "original_odds",
                "current_odds",
                "goal_odds",
                "scores",
            ])
            writer.writerow([
                "001",
                "测试主队",
                "测试客队",
                "1.80",
                "3.50",
                "4.20",
                "80",
                "10",
                "8,4.5,3.2,3.8,5.5",
                "1:0=8.5,2:0=8.0",
            ])
            temp_path = handle.name

        try:
            data = load_match_from_csv(temp_path)
            self.assertEqual(data["match_id"], "001")
            self.assertEqual(data["home_team"], "测试主队")
            self.assertEqual(data["direction"]["win"], 1.8)
            self.assertEqual(data["compression"]["original"], 80.0)
            self.assertEqual(data["goals"]["0"], 8.0)
            self.assertEqual(data["scores"]["1:0"], 8.5)
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
