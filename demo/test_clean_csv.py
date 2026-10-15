import csv
from pathlib import Path
import tempfile
import unittest

from clean_csv import INPUT_COLUMNS, InputError, run_workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.merged = self.directory / "merged.csv"
        self.rejected = self.directory / "rejected.csv"

    def write_input(self, name, rows, columns=INPUT_COLUMNS):
        path = self.directory / name
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(columns)
            writer.writerows(rows)
        return path

    def read_output(self, path):
        with path.open(encoding="utf-8", newline="") as source:
            return list(csv.DictReader(source))

    def test_duplicate_across_files_keeps_first_accepted_row_and_reason(self):
        first = self.write_input("a.csv", [[" 0007 ", " Ana ", "a@example.com", "active", "City"]])
        second = self.write_input("b.csv", [["0007", "Other", "b@example.com", "active", "City"]])
        counts = run_workflow([first, second], self.merged, self.rejected)
        self.assertEqual(counts, {"read": 2, "accepted": 1, "rejected": 1})
        self.assertEqual(self.read_output(self.merged)[0]["name"], "Ana")
        rejected = self.read_output(self.rejected)[0]
        self.assertEqual(rejected["reason"], "duplicate_customer_id")
        self.assertEqual(rejected["source_file"], "b.csv")
        self.assertEqual(rejected["source_line"], "2")
        self.assertEqual(rejected["name"], "Other")

    def test_leading_zeroes_are_preserved_and_distinct_from_numeric_lookalike(self):
        source = self.write_input("ids.csv", [
            ["0001", "A", "a@example.com", "active", "City"],
            ["1", "B", "b@example.com", "active", "City"],
        ])
        run_workflow([source], self.merged, self.rejected)
        self.assertEqual([row["customer_id"] for row in self.read_output(self.merged)], ["0001", "1"])
        self.assertEqual(self.read_output(self.rejected), [])

    def test_incompatible_header_leaves_existing_outputs_untouched(self):
        valid = self.write_input("valid.csv", [["0001", "A", "a@example.com", "active", "City"]])
        incompatible = self.write_input("wrong.csv", [], ["id", "name"])
        self.merged.write_text("existing merged", encoding="utf-8")
        self.rejected.write_text("existing rejected", encoding="utf-8")
        with self.assertRaisesRegex(InputError, "expected header"):
            run_workflow([valid, incompatible], self.merged, self.rejected)
        self.assertEqual(self.merged.read_text(encoding="utf-8"), "existing merged")
        self.assertEqual(self.rejected.read_text(encoding="utf-8"), "existing rejected")

    def test_filter_does_not_reserve_key_and_missing_key_has_own_reason(self):
        source = self.write_input("rows.csv", [
            ["0001", "Inactive", "a@example.com", "inactive", "City"],
            ["0001", "Active", "b@example.com", "active", "City"],
            [" ", "Missing", "c@example.com", "active", "City"],
        ])
        counts = run_workflow([source], self.merged, self.rejected)
        self.assertEqual(counts, {"read": 3, "accepted": 1, "rejected": 2})
        self.assertEqual(self.read_output(self.merged)[0]["name"], "Active")
        self.assertEqual([row["reason"] for row in self.read_output(self.rejected)],
                         ["filtered_status", "missing_customer_id"])

    def test_wrong_field_count_creates_no_outputs(self):
        source = self.write_input("short.csv", [["0001", "A"]])
        with self.assertRaisesRegex(InputError, "expected 5 fields"):
            run_workflow([source], self.merged, self.rejected)
        self.assertFalse(self.merged.exists())
        self.assertFalse(self.rejected.exists())

    def test_output_cannot_overwrite_input(self):
        source = self.write_input("input.csv", [["0001", "A", "a@example.com", "active", "City"]])
        original = source.read_bytes()
        with self.assertRaisesRegex(InputError, "must not overwrite"):
            run_workflow([source], source, self.rejected)
        self.assertEqual(source.read_bytes(), original)

    def test_sample_result_is_reproducible(self):
        sample_dir = Path(__file__).resolve().parent / "samples"
        counts = run_workflow([sample_dir / "customers_a.csv", sample_dir / "customers_b.csv"],
                              self.merged, self.rejected)
        self.assertEqual(counts, {"read": 8, "accepted": 5, "rejected": 3})
        self.assertEqual([row["customer_id"] for row in self.read_output(self.merged)],
                         ["0001", "0003", "0004", "0005", "1"])
        for filename, actual in [("merged.csv", self.merged), ("rejected.csv", self.rejected)]:
            expected = (Path(__file__).resolve().parent / "expected" / filename).read_bytes()
            self.assertEqual(actual.read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()
