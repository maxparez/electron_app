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
    _write_records_to_sheet,
    export_records_to_excel,
    export_records_to_esf_csv,
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
        forma="neakreditovaný kurz",
        topic="umela inteligence",
    )
    working = CertificateRecord(
        surname="Novakova",
        name="Jana",
        birth_date="05.09.1980",
        course_name="Kurz AI ve vyuce - upraveno",
        completion_date="15.03.2024",
        hours="16",
        forma="stáž",
        topic="well-being a psychohygiena",
        sablona="vzdělávání ZŠ_2_II_4",
    )
    return {
        "extracted_record": {
            "surname": extracted.surname,
            "name": extracted.name,
            "birth_date": extracted.birth_date,
            "course_name": extracted.course_name,
            "completion_date": extracted.completion_date,
            "hours": extracted.hours,
            "forma": extracted.forma,
            "sablona": extracted.sablona,
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
            "forma": working.forma,
            "sablona": working.sablona,
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
    def test_write_records_to_sheet_writes_header_and_rows_without_sheet_protection_handling(self) -> None:
        class FakeSheetApi:
            def __init__(self) -> None:
                self.ProtectContents = True
                self.unprotect_calls = 0
                self.protect_calls = 0

            def Unprotect(self) -> None:
                self.unprotect_calls += 1
                self.ProtectContents = False

            def Protect(self) -> None:
                self.protect_calls += 1
                self.ProtectContents = True

        class FakeRange:
            def __init__(self) -> None:
                self.value = None
                self.cleared = False

            def clear_contents(self) -> None:
                self.cleared = True

        class FakeSheet:
            def __init__(self) -> None:
                self.api = FakeSheetApi()
                self.ranges = {}

            def range(self, address: str) -> FakeRange:
                if address not in self.ranges:
                    self.ranges[address] = FakeRange()
                return self.ranges[address]

        sheet = FakeSheet()
        records = [
            CertificateRecord(
                surname="Novakova",
                name="Jana",
                birth_date="05.09.1980",
                course_name="Kurz AI ve vyuce",
                completion_date="14.03.2024",
                hours="8",
                forma="akreditovaný kurz průběžné DVPP",
                sablona="vzdělávání ZŠ_2_II_4",
                topic="umělá inteligence",
            )
        ]

        _write_records_to_sheet(sheet, records, build_export_metadata())

        self.assertEqual(0, sheet.api.unprotect_calls)
        self.assertEqual(0, sheet.api.protect_calls)
        self.assertEqual("CZ.00/00/00/00000", sheet.ranges["D6"].value)
        self.assertEqual("1", sheet.ranges["I6"].value)
        self.assertEqual("Zakladni skola Test", sheet.ranges["D7"].value)
        self.assertTrue(sheet.ranges["B11:J500"].cleared)
        self.assertEqual(
            [[
                "Novakova",
                "Jana",
                "vzdělávání ZŠ_2_II_4",
                "Kurz AI ve vyuce",
                "14.03.2024",
                "8",
                "akreditovaný kurz průběžné DVPP",
                "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
                "",
            ]],
            sheet.ranges["B11"].value,
        )

    def test_write_records_to_sheet_leaves_unprotected_sheet_unprotected(self) -> None:
        class FakeSheetApi:
            def __init__(self) -> None:
                self.ProtectContents = False
                self.unprotect_calls = 0
                self.protect_calls = 0

            def Unprotect(self) -> None:
                self.unprotect_calls += 1

            def Protect(self) -> None:
                self.protect_calls += 1

        class FakeRange:
            def __init__(self) -> None:
                self.value = None

            def clear_contents(self) -> None:
                pass

        class FakeSheet:
            def __init__(self) -> None:
                self.api = FakeSheetApi()
                self.ranges = {}

            def range(self, address: str) -> FakeRange:
                if address not in self.ranges:
                    self.ranges[address] = FakeRange()
                return self.ranges[address]

        sheet = FakeSheet()
        _write_records_to_sheet(sheet, [], build_export_metadata(fill_header=False))
        self.assertEqual(0, sheet.api.unprotect_calls)
        self.assertEqual(0, sheet.api.protect_calls)

    def test_export_records_to_tsv_uses_working_record_values(self) -> None:
        record = build_working_record_payload()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "records.tsv"
            result = export_records_to_tsv([record], output_path=str(output_path))

            self.assertEqual(str(output_path), result["output_path"])
            self.assertTrue(output_path.exists())
            self.assertIn("Kurz AI ve vyuce - upraveno", output_path.read_text(encoding="utf-8"))
            self.assertIn("15.03.2024", result["content"])
            self.assertIn("vzdělávání ZŠ_2_II_4", result["content"])
            self.assertIn("stáž", result["content"])

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
            self.assertEqual("vzdělávání ZŠ_2_II_4", writer_calls[0][1][0].sablona)

    def test_export_records_to_excel_allows_partial_metadata_when_header_enabled(self) -> None:
        record = build_working_record_payload()
        metadata = build_export_metadata(project_number="")
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
        self.assertEqual("", writer_calls[0][2].project_number)

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

    def test_export_records_to_esf_csv_writes_header_and_keeps_all_columns(self) -> None:
        record = build_working_record_payload()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "osoby.csv"
            result = export_records_to_esf_csv([record], output_path=str(output_path))

            self.assertEqual(str(output_path), result["output_path"])
            self.assertTrue(output_path.exists())

            content = output_path.read_text(encoding="utf-8-sig")
            lines = content.splitlines()
            self.assertEqual(2, len(lines))

            header = lines[0].split(";")
            row = lines[1].split(";")
            self.assertEqual(32, len(header))
            self.assertEqual(32, len(row))
            self.assertEqual("Jmeno_Osoby", header[0])
            self.assertEqual("Prijmeni_Osoby", header[1])
            self.assertEqual("DatumNarozeni_Osoby", header[2])
            self.assertEqual("Jana", row[0])
            self.assertEqual("Novakova", row[1])
            self.assertEqual("05.09.1980", row[2])
            self.assertEqual("Aš", row[3])
            self.assertEqual("Aš", row[4])
            self.assertEqual("Saská", row[5])
            self.assertEqual("24", row[6])
            self.assertEqual("1", row[7])
            self.assertEqual("", row[8])
            self.assertEqual("35201", row[9])
            self.assertEqual("01.09.2025", row[16])
            self.assertEqual("POHMUZI", row[17])
            self.assertEqual("TPZAMCI", row[18])
            self.assertEqual("", row[19])
            self.assertEqual("VZISCED5-8", row[20])
            self.assertTrue(lines[1].endswith(";;;;;;;;;;;"))

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

    def test_server_excel_export_endpoint_prefers_specific_processor_error(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def export_excel(self, records_payload, export_metadata_payload, template_path=None, output_path=None):
                return {
                    "success": False,
                    "data": None,
                    "errors": ["Missing required export metadata: project_number"],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/dvpp-certificates/export/excel",
                json={
                    "records": [build_working_record_payload()],
                    "exportMetadata": asdict(build_export_metadata(project_number="")),
                    "templatePath": "/tmp/template.xlsx",
                    "outputPath": "/tmp/output.xlsx",
                },
            )

        self.assertEqual(400, response.status_code)
        payload = response.get_json()
        self.assertEqual("error", payload["status"])
        self.assertEqual(
            "Missing required export metadata: project_number",
            payload["message"],
        )

    def test_server_esf_export_endpoint_returns_processor_payload(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def export_esf(self, records_payload, output_path=None):
                return {
                    "success": True,
                    "data": {
                        "content": "Jmeno_Osoby;Prijmeni_Osoby\nJana;Novakova",
                        "output_path": output_path,
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/dvpp-certificates/export/esf",
                json={
                    "records": [build_working_record_payload()],
                    "outputPath": "/tmp/osoby.csv",
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("success", payload["status"])
        self.assertEqual("/tmp/osoby.csv", payload["data"]["output_path"])


if __name__ == "__main__":
    unittest.main()
