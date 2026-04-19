#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_certificates.domain import CertificateRecord, RecordOrigin
from dvpp_certificates.normalization import (
    TOPIC_CATALOG,
    normalize_certificate_fields,
    normalize_date,
    normalize_topic,
    strip_titles,
)


class DvppCertificatesNormalizationTests(unittest.TestCase):
    def test_topic_catalog_matches_expected_values(self) -> None:
        self.assertEqual(
            (
                "pedagogická diagnostika",
                "individualizace vzdělávání",
                "formativní hodnocení",
                "podpora nadání/talentu",
                "řečová výchova",
                "grafomotorika",
                "rozvoj gramotností",
                "rozvoj digitálních kompetencí",
                "podpora polytechniky",
                "vzdělávání pro udržitelný rozvoj – např. EVVO, klimatické vzdělávání, principy místně zakotveného učení",
                "well-being a psychohygiena",
                "genderová tematika v obsahu vzdělávání",
                "výuka moderních dějin",
                "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
                "pohybové aktivity",
                "práce s dětmi/žáky se speciálními vzdělávacími potřebami; vzdělávání heterogenních kolektivů",
                "vzdělávání dětí/žáků cizinců a dětí/žáků s potřebou jazykové podpory",
                "rozvoj pedagogických kompetencí v oblasti metod a forem vzdělávání",
                "komunikace se zákonnými zástupci",
                "management škol, řízení organizace, leadership a řízení pedagogického procesu",
                "vzdělávání dětí a žáků z marginalizovaných skupin, jako jsou Romové",
                "podpora uvádějících/provázejících učitelů",
                "profesní rozvoj ostatních pracovníků ve vzdělávání",
            ),
            TOPIC_CATALOG,
        )

    def test_strip_titles_removes_academic_prefixes_and_suffixes(self) -> None:
        self.assertEqual("Jana", strip_titles("Mgr. Jana, Ph.D."))
        self.assertEqual("Novakova", strip_titles("Bc. Novakova, DiS."))

    def test_normalize_date_preserves_uncertainty_marker(self) -> None:
        self.assertEqual("07.03.2024", normalize_date("2024-03-07"))
        self.assertEqual("07.03.2024?", normalize_date("07/03/2024?"))

    def test_normalize_topic_enforces_whitelist(self) -> None:
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            normalize_topic("umela inteligence"),
        )
        self.assertEqual("formativní hodnocení", normalize_topic("formativní hodnocení"))
        self.assertEqual("formativní hodnocení", normalize_topic("formativni hodnoceni"))
        self.assertEqual(
            "management škol, řízení organizace, leadership a řízení pedagogického procesu",
            normalize_topic("management skol, rizeni organizace, leadership a rizeni pedagogickeho procesu"),
        )
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            normalize_topic("medialni gramotnost, prevence kybersikany, chovani na socialnich sitich, umela inteligence"),
        )
        self.assertEqual(
            "profesní rozvoj ostatních pracovníků ve vzdělávání",
            normalize_topic("profesni rozvoj ostatnich pracovniku ve vzdelavani"),
        )
        self.assertEqual("", normalize_topic("finance a ucetnictvi"))

    def test_normalize_certificate_fields_returns_canonical_record(self) -> None:
        origin = RecordOrigin(
            source_mode="gemini",
            source_file="certificates/sample.pdf",
            model_name="gemini-3-flash-preview",
        )

        record = normalize_certificate_fields(
            {
                "surname": "Bc. Novakova, DiS.",
                "name": "Mgr. Jana, Ph.D.",
                "birth_date": "1980-09-05",
                "course_name": "Kurz AI ve vyuce",
                "completion_date": "14/03/2024",
                "hours": " 8 ",
                "sablona": "vzdělávání ZŠ_2_II_4",
                "topic": "umela inteligence",
                "uncertainty_notes": "  low-confidence surname  ",
            },
            origin=origin,
        )

        self.assertIsInstance(record, CertificateRecord)
        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)
        self.assertEqual("05.09.1980", record.birth_date)
        self.assertEqual("14.03.2024", record.completion_date)
        self.assertEqual("8", record.hours)
        self.assertEqual("vzdělávání ZŠ_2_II_4", record.sablona)
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            record.topic,
        )
        self.assertEqual("low-confidence surname", record.uncertainty_notes)
        self.assertIs(record.origin, origin)

    def test_normalize_certificate_fields_rejects_non_string_required_values(self) -> None:
        with self.assertRaises(TypeError) as exc_info:
            normalize_certificate_fields(
                {
                    "surname": None,
                    "name": "Jana",
                    "birth_date": "1980-09-05",
                    "course_name": "Kurz AI ve vyuce",
                    "completion_date": "14/03/2024",
                    "hours": "8",
                }
            )

        self.assertIn("surname", str(exc_info.exception))

    def test_normalize_certificate_fields_rejects_missing_required_keys_cleanly(self) -> None:
        with self.assertRaises(TypeError) as exc_info:
            normalize_certificate_fields(
                {
                    "surname": "Novakova",
                    "birth_date": "1980-09-05",
                    "course_name": "Kurz AI ve vyuce",
                    "completion_date": "14/03/2024",
                    "hours": "8",
                }
            )

        self.assertIn("name", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
