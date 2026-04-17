#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_cert_extraction import (
    CertificateRecord,
    ExtractionResult,
    build_extraction_prompt,
    format_tsv_row,
    normalize_date,
    normalize_topic,
    strip_titles,
)


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

    def test_certificate_record_validates_required_fields(self) -> None:
        record = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)
        self.assertEqual("05.09.1980", record.birth_date)
        self.assertEqual("Kurz AI ve vyuce", record.course_name)
        self.assertEqual("14.03.2024", record.completion_date)
        self.assertEqual("8", record.hours)
        self.assertEqual("umela inteligence", record.topic)

        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="",
                name="Jana",
                birth_date="05.09.1980",
                course_name="Kurz AI ve vyuce",
                completion_date="14.03.2024",
                hours="8",
                topic="umela inteligence",
            )

    def test_certificate_record_rejects_invalid_dates(self) -> None:
        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="Novakova",
                name="Jana",
                birth_date="1980/99/99",
                course_name="Kurz AI ve vyuce",
                completion_date="14.03.2024",
                hours="8",
                topic="umela inteligence",
            )

        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="Novakova",
                name="Jana",
                birth_date="05.09.1980",
                course_name="Kurz AI ve vyuce",
                completion_date="31.02.2024",
                hours="8",
                topic="umela inteligence",
            )

    def test_certificate_record_allows_uncertain_dates_with_question_mark(self) -> None:
        record = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980?",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024?",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("05.09.1980?", record.birth_date)
        self.assertEqual("14.03.2024?", record.completion_date)

    def test_certificate_record_strips_titles_from_name_and_surname(self) -> None:
        record = CertificateRecord(
            surname="Bc. Novakova, DiS.",
            name="Mgr. Jana, Ph.D.",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)

    def test_extraction_result_requires_certificate_list(self) -> None:
        result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Novakova",
                    name="Jana",
                    birth_date="05.09.1980",
                    course_name="Kurz AI ve vyuce",
                    completion_date="14.03.2024",
                    hours="8",
                    topic="umela inteligence",
                )
            ]
        )

        self.assertEqual(1, len(result.certificates))
        self.assertEqual("Novakova", result.certificates[0].surname)

        with self.assertRaises(TypeError):
            ExtractionResult(certificates="not-a-list")

    def test_extraction_result_rejects_non_certificate_item(self) -> None:
        with self.assertRaises(TypeError):
            ExtractionResult(certificates=["not-a-record"])

    def test_build_extraction_prompt_includes_required_instructions_and_topic_catalog(self) -> None:
        prompt = build_extraction_prompt()

        self.assertIn('Jsi "Certifikator v2.1"', prompt)
        self.assertIn("Datum narozeni", prompt)
        self.assertIn("Pokud si jakymkoli udajem", prompt)
        self.assertIn(
            "Prijmeni<TAB>Jmeno<TAB>Datum narozeni<TAB>Nazev kurzu<TAB>Datum ukonceni vzdelavani<TAB>Pocet hodin<TAB><TAB>Tema",
            prompt,
        )
        self.assertIn("umela inteligence", prompt)
        self.assertIn("pedagogicka diagnostika", prompt)
        self.assertIn("well-being a psychohygiena", prompt)
        self.assertIn("podpora uvadejicich/provazejicich ucitelu", prompt)


if __name__ == "__main__":
    unittest.main()
