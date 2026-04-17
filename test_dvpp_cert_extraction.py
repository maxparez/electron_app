#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_cert_extraction import format_tsv_row, normalize_date, normalize_topic, strip_titles


class DvppCertExtractionTests(unittest.TestCase):
    def test_format_tsv_row_uses_expected_field_order(self) -> None:
        record = {
            "surname": "Novakova",
            "name": "Jana",
            "birth_date": "05.09.1980",
            "course_name": "Kurz AI ve vyuce",
            "completion_date": "14.03.2024",
            "hours": "8",
            "topic": "umela inteligence",
        }

        self.assertEqual(
            "Novakova\tJana\t05.09.1980\tKurz AI ve vyuce\t14.03.2024\t8\t\tumela inteligence",
            format_tsv_row(record),
        )

    def test_normalize_topic_enforces_whitelist(self) -> None:
        self.assertEqual("umela inteligence", normalize_topic("umela inteligence"))
        self.assertEqual("", normalize_topic("finance a ucetnictvi"))

    def test_normalize_date_returns_dd_mm_yyyy(self) -> None:
        self.assertEqual("07.03.2024", normalize_date("2024-03-07"))
        self.assertEqual("07.03.2024", normalize_date("7.3.2024"))
        self.assertEqual("07.03.2024", normalize_date("07/03/2024"))

    def test_strip_titles_removes_academic_prefixes_and_suffixes(self) -> None:
        self.assertEqual("Jana", strip_titles("Mgr. Jana, Ph.D."))
        self.assertEqual("Novakova", strip_titles("Bc. Novakova, DiS."))


if __name__ == "__main__":
    unittest.main()
