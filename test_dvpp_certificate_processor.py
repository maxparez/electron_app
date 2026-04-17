#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

import server

from dvpp_cert_extraction import ExtractionResult
from dvpp_certificates.domain import CertificateRecord
from tools.dvpp_certificate_processor import DvppCertificateProcessor


def build_certificate(*, surname: str, name: str) -> CertificateRecord:
    return CertificateRecord(
        surname=surname,
        name=name,
        birth_date="05.09.1980",
        course_name="Kurz AI ve vyuce",
        completion_date="14.03.2024",
        hours="8",
        topic="umela inteligence",
    )


class RecordingImporter:
    def __init__(self, failing_files: set[str] | None = None) -> None:
        self.calls: list[tuple[str, str, str | None]] = []
        self.failing_files = failing_files or set()

    def import_file(self, file_path: str, *, model_name: str, api_key: str | None = None, env=None):
        self.calls.append((file_path, model_name, api_key))
        if Path(file_path).name in self.failing_files:
            raise ValueError("Malformed extraction response")
        return ExtractionResult(
            certificates=[
                build_certificate(surname=f"Surname {Path(file_path).stem}", name="Jana"),
            ]
        )


class DvppCertificateProcessorTests(unittest.TestCase):
    def test_process_imports_directory_as_one_file_per_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            first = project_dir / "a.pdf"
            second = project_dir / "nested" / "b.png"
            first.write_bytes(b"%PDF-1.4")
            second.parent.mkdir(parents=True)
            second.write_bytes(b"PNG")

            importer = RecordingImporter()
            processor = DvppCertificateProcessor(importer=importer)

            result = processor.process(
                [],
                {
                    "folder_path": str(project_dir),
                    "model_name": "gemini-3-flash-preview",
                    "api_key": "test-key",
                },
            )

            self.assertTrue(result["success"])
            self.assertEqual(
                [
                    (str(first.resolve()), "gemini-3-flash-preview", "test-key"),
                    (str(second.resolve()), "gemini-3-flash-preview", "test-key"),
                ],
                importer.calls,
            )
            self.assertEqual(2, result["data"]["processedFiles"])
            self.assertEqual(2, result["data"]["successfulFiles"])
            self.assertEqual(0, result["data"]["failedFiles"])
            self.assertEqual(2, len(result["data"]["batch"]["records"]))
            self.assertEqual("gemini", result["data"]["batch"]["input_mode"])
            self.assertEqual(str(project_dir), result["data"]["batch"]["source_folder"])
            self.assertEqual(str(first.resolve()), result["data"]["batch"]["records"][0]["extracted_record"]["origin"]["source_file"])

    def test_process_collects_per_file_errors_and_keeps_successful_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            good_file = project_dir / "good.pdf"
            bad_file = project_dir / "bad.pdf"
            good_file.write_bytes(b"%PDF-1.4")
            bad_file.write_bytes(b"%PDF-1.4")

            importer = RecordingImporter(failing_files={"bad.pdf"})
            processor = DvppCertificateProcessor(importer=importer)

            result = processor.process(
                [str(good_file), str(bad_file)],
                {
                    "folder_path": str(project_dir),
                    "model_name": "gemini-3-flash-preview",
                    "api_key": "test-key",
                },
            )

            self.assertTrue(result["success"])
            self.assertEqual(1, result["data"]["successfulFiles"])
            self.assertEqual(1, result["data"]["failedFiles"])
            self.assertEqual(2, len(result["data"]["diagnostics"]))
            self.assertEqual([], result["data"]["diagnostics"][0]["errors"])
            self.assertEqual(["Malformed extraction response"], result["data"]["diagnostics"][1]["errors"])
            self.assertEqual(1, len(result["data"]["batch"]["records"]))
            self.assertTrue(result["warnings"])

    def test_process_fails_when_all_files_return_malformed_responses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            broken_file = project_dir / "broken.pdf"
            broken_file.write_bytes(b"%PDF-1.4")

            importer = RecordingImporter(failing_files={"broken.pdf"})
            processor = DvppCertificateProcessor(importer=importer)

            result = processor.process(
                [],
                {
                    "folder_path": str(project_dir),
                    "model_name": "gemini-3-flash-preview",
                    "api_key": "test-key",
                },
            )

            self.assertFalse(result["success"])
            self.assertEqual(1, result["data"]["failedFiles"])
            self.assertEqual(0, len(result["data"]["batch"]["records"]))
            self.assertIn("Nepodařilo se vytěžit žádné certifikáty", result["errors"])

    def test_server_endpoint_returns_processor_payload(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def process(self, files, options):
                return {
                    "success": True,
                    "data": {
                        "batch": {
                            "input_mode": "gemini",
                            "source_folder": options["folder_path"],
                            "records": [],
                            "warnings": [],
                            "errors": [],
                            "export_metadata": {},
                        },
                        "diagnostics": [],
                        "processedFiles": len(files),
                        "successfulFiles": len(files),
                        "failedFiles": 0,
                        "modelName": options["model_name"],
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            file_path = project_dir / "one.pdf"
            file_path.write_bytes(b"%PDF-1.4")

            with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
                response = server.app.test_client().post(
                    "/api/dvpp-certificates/import/gemini",
                    json={
                        "folderPath": str(project_dir),
                        "selectedFiles": [str(file_path)],
                        "modelName": "gemini-3-flash-preview",
                        "apiKey": "test-key",
                    },
                )

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("success", payload["status"])
        self.assertEqual(1, payload["data"]["processedFiles"])
        self.assertEqual("gemini-3-flash-preview", payload["data"]["modelName"])

    def test_import_raw_text_returns_shared_batch_payload(self) -> None:
        processor = DvppCertificateProcessor(importer=RecordingImporter())

        result = processor.import_raw_text(
            "Novakova\tJana\t05.09.1980\tKurz AI ve vyuce\t14.03.2024\t8\t\tumela inteligence"
        )

        self.assertTrue(result["success"])
        self.assertEqual("raw_text", result["data"]["batch"]["input_mode"])
        self.assertEqual(1, len(result["data"]["batch"]["records"]))
        self.assertEqual(1, result["data"]["processedRows"])

    def test_server_raw_text_endpoint_returns_processor_payload(self) -> None:
        class FakeProcessor:
            def __init__(self, logger, importer=None) -> None:
                self.logger = logger

            def import_raw_text(self, raw_text):
                return {
                    "success": True,
                    "data": {
                        "batch": {
                            "input_mode": "raw_text",
                            "source_folder": "",
                            "records": [],
                            "warnings": [],
                            "errors": [],
                            "export_metadata": {},
                        },
                        "processedRows": 1,
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "DvppCertificateProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/dvpp-certificates/import/raw-text",
                json={"rawText": "Novakova\tJana\t05.09.1980\tKurz\t14.03.2024\t8\t\tumela inteligence"},
            )

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("success", payload["status"])
        self.assertEqual(1, payload["data"]["processedRows"])


if __name__ == "__main__":
    unittest.main()
