#!/usr/bin/env python3

import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

import server

from dvpp_certificates.domain import CertificateRecord, ExportMetadata
from dvpp_certificates.exporters import (
    DEFAULT_EXCEL_TEMPLATE_PATH,
    export_records_to_excel,
    export_records_to_tsv,
    resolve_excel_template_path,
)


def build_working_record_payload() -> dict:
    extracted = CertificateRecord(
        surname="Novakova",
        name="Jana",
        birth_date="05.09.1980",
        course_name="Kurz AI ve vyuce",
        completion_date="14.03.2024",
        hours="8",
        topic="umela inteligence",
    )
    working = CertificateRecord(
        surname="Novakova",
        name="Jana",
        birth_date="05.09.1980",
        course_name="Kurz AI ve vyuce - upraveno",
        completion_date="15.03.2024",
        hours="16",
        topic="well-being a psychohygiena",
    )
    return {
        "extracted_record": {
            "surname": extracted.surname,
            "name": extracted.name,
            "birth_date": extracted.birth_date,
            "course_name": extracted.course_name,
            "completion_date": extracted.completion_date,
            "hours": extracted.hours,
            "topic": extracted.topic,
            "uncertainty_notes": extracted.uncertainty_notes,
            "origin": None,
        },
        "working_record": {
            "surname": working.surname,
            "name": working.name,
            "birth_date": working.birth_date,
            "course_name": working.course_name,
            "completion_date": working.completion_date,
            "hours": working.hours,
            "topic": working.topic,
            "uncertainty_notes": working.uncertainty_notes,
            "origin": None,
        },
    }


def build_export_metadata(**overrides) -> ExportMetadata:
    payload = {
        "project_number": "CZ.00/00/00/00000",
        "recipient_name": "Zakladni skola Test",
        "zor_number": "1",
        "fill_header": True,
    }
    payload.update(overrides)
    return ExportMetadata(**payload)


class DvppCertificateExportersTests(unittest.TestCase):
    def test_export_records_to_tsv_uses_working_record_values(self) -> None:
        record = build_working_record_payload()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "records.tsv"
            result = export_records_to_tsv([record], output_path=str(output_path))

            self.assertEqual(str(output_path), result["output_path"])
            self.assertTrue(output_path.exists())
            self.assertIn("Kurz AI ve vyuce - upraveno", output_path.read_text(encoding="utf-8"))
            self.assertIn("15.03.2024", result["content"])

    def test_export_records_to_excel_copies_template_without_overwriting_source(self) -> None:
        record = build_working_record_payload()
        metadata = build_export_metadata()
        writer_calls = []

        def fake_writer(output_path, records, export_metadata):
            writer_calls.append((output_path, records, export_metadata))

        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "template.xlsx"
            template_path.write_bytes(b"template-bytes")

            output_path = export_records_to_excel(
                [record],
                metadata,
                template_path=str(template_path),
                workbook_writer=fake_writer,
            )

            self.assertTrue(Path(output_path).exists())
            self.assertNotEqual(str(template_path), output_path)
            self.assertEqual(b"template-bytes", template_path.read_bytes())
            self.assertEqual(1, len(writer_calls))
            self.assertEqual(output_path, writer_calls[0][0])

    def test_export_records_to_excel_requires_metadata_before_write_when_header_enabled(self) -> None:
        record = build_working_record_payload()
        metadata = build_export_metadata(project_number="")
        writer_called = False

        def fake_writer(output_path, records, export_metadata):
            nonlocal writer_called
            writer_called = True

        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "template.xlsx"
            template_path.write_bytes(b"template-bytes")

            with self.assertRaises(ValueError) as exc_info:
                export_records_to_excel(
                    [record],
                    metadata,
                    template_path=str(template_path),
                    workbook_writer=fake_writer,
                )

        self.assertIn("project_number", str(exc_info.exception))
        self.assertFalse(writer_called)

    def test_export_records_to_excel_allows_blank_header_fields_when_header_disabled(self) -> None:
        record = build_working_record_payload()
        metadata = build_export_metadata(
            project_number="",
            recipient_name="",
            zor_number="",
            fill_header=False,
        )
        writer_calls = []

        def fake_writer(output_path, records, export_metadata):
            writer_calls.append((output_path, records, export_metadata))

        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = Path(temp_dir) / "template.xlsx"
            template_path.write_bytes(b"template-bytes")

            output_path = export_records_to_excel(
                [record],
                metadata,
                template_path=str(template_path),
                workbook_writer=fake_writer,
            )

        self.assertEqual(1, len(writer_calls))
        self.assertEqual(output_path, writer_calls[0][0])

    def test_resolve_excel_template_path_uses_default_template(self) -> None:
        self.assertEqual(DEFAULT_EXCEL_TEMPLATE_PATH, resolve_excel_template_path(None))

    def test_server_tsv_export_endpoint_returns_processor_payload(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def export_tsv(self, records_payload, output_path=None):
                return {
                    "success": True,
                    "data": {
                        "content": "Novakova\tJana",
                        "output_path": output_path,
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/dvpp-certificates/export/tsv",
                json={
                    "records": [build_working_record_payload()],
                    "outputPath": "/tmp/out.tsv",
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("success", payload["status"])
        self.assertEqual("/tmp/out.tsv", payload["data"]["output_path"])

    def test_server_excel_export_endpoint_returns_processor_payload(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def export_excel(self, records_payload, export_metadata_payload, template_path=None, output_path=None):
                return {
                    "success": True,
                    "data": {
                        "output_path": output_path,
                        "template_path": template_path,
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/dvpp-certificates/export/excel",
                json={
                    "records": [build_working_record_payload()],
                    "exportMetadata": asdict(build_export_metadata()),
                    "templatePath": "/tmp/template.xlsx",
                    "outputPath": "/tmp/output.xlsx",
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("success", payload["status"])
        self.assertEqual("/tmp/output.xlsx", payload["data"]["output_path"])


if __name__ == "__main__":
    unittest.main()
