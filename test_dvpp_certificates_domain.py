#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_certificates.domain import (
    CertificateRecord,
    ExportMetadata,
    ExtractionBatch,
    RecordOrigin,
    WorkingRecord,
)


class DvppCertificatesDomainTests(unittest.TestCase):
    def test_certificate_record_exposes_canonical_fields(self) -> None:
        origin = RecordOrigin(
            source_mode="gemini",
            source_file="certificates/sample.pdf",
            model_name="gemini-3-flash-preview",
        )

        record = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
            uncertainty_notes="birth date read from low-quality scan",
            origin=origin,
        )

        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)
        self.assertEqual("05.09.1980", record.birth_date)
        self.assertEqual("Kurz AI ve vyuce", record.course_name)
        self.assertEqual("14.03.2024", record.completion_date)
        self.assertEqual("8", record.hours)
        self.assertEqual("", record.forma)
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            record.topic,
        )
        self.assertEqual("", record.sablona)
        self.assertEqual("birth date read from low-quality scan", record.uncertainty_notes)
        self.assertIs(record.origin, origin)

    def test_record_origin_keeps_provenance_fields(self) -> None:
        origin = RecordOrigin(
            source_mode="raw_text",
            source_file="manual-import.txt",
            raw_row="Novakova\tJana\t05.09.1980\tKurz\t14.03.2024\t8\t\t",
            model_name="",
            source_index=3,
        )

        self.assertEqual("raw_text", origin.source_mode)
        self.assertEqual("manual-import.txt", origin.source_file)
        self.assertEqual(
            "Novakova\tJana\t05.09.1980\tKurz\t14.03.2024\t8\t\t",
            origin.raw_row,
        )
        self.assertEqual("", origin.model_name)
        self.assertEqual(3, origin.source_index)

    def test_working_record_preserves_extracted_and_editable_values(self) -> None:
        extracted = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
        )

        working = WorkingRecord(extracted_record=extracted)
        working.working_record.course_name = "Kurz AI ve vyuce - opraveno"
        working.working_record.hours = "16"

        self.assertEqual("Kurz AI ve vyuce", working.extracted_record.course_name)
        self.assertEqual("8", working.extracted_record.hours)
        self.assertEqual("Kurz AI ve vyuce - opraveno", working.working_record.course_name)
        self.assertEqual("16", working.working_record.hours)
        self.assertIsNot(working.extracted_record, working.working_record)

    def test_working_record_deep_copies_origin_for_editable_record(self) -> None:
        extracted = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            origin=RecordOrigin(
                source_mode="gemini",
                source_file="certificates/sample.pdf",
                model_name="gemini-3-flash-preview",
            ),
        )

        working = WorkingRecord(extracted_record=extracted)
        working.working_record.origin.source_file = "certificates/edited.pdf"

        self.assertEqual(
            "certificates/sample.pdf",
            working.extracted_record.origin.source_file,
        )
        self.assertEqual(
            "certificates/edited.pdf",
            working.working_record.origin.source_file,
        )
        self.assertIsNot(working.extracted_record.origin, working.working_record.origin)

    def test_working_record_rejects_mismatched_supplied_working_record(self) -> None:
        extracted = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
        )
        unrelated = CertificateRecord(
            surname="Svobodova",
            name="Petra",
            birth_date="01.01.1990",
            course_name="Jiny kurz",
            completion_date="01.02.2024",
            hours="16",
        )

        with self.assertRaises(ValueError):
            WorkingRecord(extracted_record=extracted, working_record=unrelated)

    def test_extraction_batch_holds_records_and_export_metadata(self) -> None:
        batch = ExtractionBatch(
            input_mode="gemini",
            source_folder="/tmp/certificates",
            records=[
                WorkingRecord(
                    extracted_record=CertificateRecord(
                        surname="Novakova",
                        name="Jana",
                        birth_date="05.09.1980",
                        course_name="Kurz AI ve vyuce",
                        completion_date="14.03.2024",
                        hours="8",
                    )
                )
            ],
            warnings=["missing topic mapping"],
            errors=[],
            export_metadata=ExportMetadata(
                template_path="D:/JAK2024/Dokumenty/template.xlsx",
                output_path="D:/JAK2024/Exports/export.xlsx",
                project_number="CZ.02.02.XX/00/00_000/0000000",
                recipient_name="Zakladni skola",
                zor_number="1ZoR",
                fill_header=True,
            ),
        )

        self.assertEqual("gemini", batch.input_mode)
        self.assertEqual("/tmp/certificates", batch.source_folder)
        self.assertEqual(1, len(batch.records))
        self.assertEqual(["missing topic mapping"], batch.warnings)
        self.assertEqual([], batch.errors)
        self.assertEqual(
            "D:/JAK2024/Dokumenty/template.xlsx",
            batch.export_metadata.template_path,
        )
        self.assertEqual(
            "CZ.02.02.XX/00/00_000/0000000",
            batch.export_metadata.project_number,
        )
        self.assertTrue(batch.export_metadata.fill_header)


if __name__ == "__main__":
    unittest.main()
