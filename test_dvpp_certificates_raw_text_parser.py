#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_certificates.domain import ExtractionBatch, WorkingRecord
from dvpp_certificates.raw_text_parser import parse_raw_text_batch


class DvppCertificatesRawTextParserTests(unittest.TestCase):
    def test_parse_raw_text_batch_returns_one_working_record_per_row(self) -> None:
        batch = parse_raw_text_batch(
            "Novakova\tJana\t05.09.1980\tvzdělávání ZŠ_2_II_4\tKurz AI ve vyuce\t14.03.2024\t8\tneakreditovaný kurz\tumela inteligence"
        )

        self.assertIsInstance(batch, ExtractionBatch)
        self.assertEqual("raw_text", batch.input_mode)
        self.assertEqual(1, len(batch.records))
        self.assertIsInstance(batch.records[0], WorkingRecord)
        self.assertEqual("Novakova", batch.records[0].extracted_record.surname)
        self.assertEqual("Jana", batch.records[0].working_record.name)
        self.assertEqual("vzdělávání ZŠ_2_II_4", batch.records[0].working_record.sablona)
        self.assertEqual("neakreditovaný kurz", batch.records[0].working_record.forma)
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            batch.records[0].working_record.topic,
        )
        self.assertEqual(
            "raw_text", batch.records[0].extracted_record.origin.source_mode
        )
        self.assertEqual(
            "Novakova\tJana\t05.09.1980\tvzdělávání ZŠ_2_II_4\tKurz AI ve vyuce\t14.03.2024\t8\tneakreditovaný kurz\tumela inteligence",
            batch.records[0].extracted_record.origin.raw_row,
        )
        self.assertEqual(1, batch.records[0].extracted_record.origin.source_index)

    def test_parse_raw_text_batch_ignores_empty_lines_only(self) -> None:
        batch = parse_raw_text_batch(
            "\n"
            "Novakova\tJana\t05.09.1980\tvzdělávání ZŠ_2_II_4\tKurz AI ve vyuce\t14.03.2024\t8\t\tumela inteligence\n"
            "\n"
            "Svobodova\tPetra\t01.01.1990\tvzdělávání MŠ_2_I_5\tKurz Wellbeing\t15.03.2024\t16\t\twell-being a psychohygiena\n"
            "\n"
        )

        self.assertEqual(2, len(batch.records))
        self.assertEqual("Novakova", batch.records[0].working_record.surname)
        self.assertEqual("Svobodova", batch.records[1].working_record.surname)
        self.assertEqual(1, batch.records[0].extracted_record.origin.source_index)
        self.assertEqual(2, batch.records[1].extracted_record.origin.source_index)

    def test_parse_raw_text_batch_keeps_backward_compatible_rows_without_sablona(self) -> None:
        batch = parse_raw_text_batch(
            "Novakova\tJana\t05.09.1980\tKurz AI ve vyuce\t14.03.2024\t8\t\tumela inteligence"
        )

        self.assertEqual(1, len(batch.records))
        self.assertEqual("", batch.records[0].working_record.sablona)
        self.assertEqual("", batch.records[0].working_record.forma)
        self.assertEqual("Kurz AI ve vyuce", batch.records[0].working_record.course_name)

    def test_parse_raw_text_batch_rejects_empty_input(self) -> None:
        with self.assertRaises(ValueError) as exc_info:
            parse_raw_text_batch(" \n\t\n")

        self.assertIn("No certificate rows", str(exc_info.exception))

    def test_parse_raw_text_batch_rejects_wrong_column_count(self) -> None:
        with self.assertRaises(ValueError) as exc_info:
            parse_raw_text_batch(
                "Novakova\tJana\t05.09.1980\tKurz AI ve vyuce\t14.03.2024\t8\tumela inteligence"
            )

        self.assertIn("line 1", str(exc_info.exception))
        self.assertIn("column count", str(exc_info.exception))

    def test_parse_raw_text_batch_accepts_forma_column(self) -> None:
        batch = parse_raw_text_batch(
            "Novakova\tJana\t05.09.1980\tvzdělávání ZŠ_2_II_4\tKurz AI ve vyuce\t14.03.2024\t8\tstáž\tumela inteligence"
        )

        self.assertEqual("stáž", batch.records[0].working_record.forma)


if __name__ == "__main__":
    unittest.main()
