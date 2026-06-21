#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

import server


def build_combined_workbook(path: Path) -> None:
    workbook = Workbook()
    first_sheet = workbook.active
    first_sheet.title = "1. ročník"
    first_sheet["B6"] = "datum aktivity"
    first_sheet["B7"] = "čas zahájení"

    second_sheet = workbook.create_sheet("2. ročník")
    second_sheet["B6"] = "datum aktivity"
    second_sheet["B7"] = "čas zahájení"
    workbook.save(path)


class AttendanceSplitterServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = server.app.test_client()

    def test_scan_endpoint_finds_candidates_in_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "combined.xlsx"
            build_combined_workbook(workbook_path)

            response = self.client.post(
                "/api/attendance-splitter/scan",
                json={"folderPath": temp_dir},
            )

            self.assertEqual(200, response.status_code)
            payload = response.get_json()
            self.assertTrue(payload["success"])
            self.assertEqual(1, len(payload["files"]))
            self.assertEqual("combined.xlsx", payload["files"][0]["name"])

    def test_scan_endpoint_accepts_selected_file_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook_path = Path(temp_dir) / "combined.xlsx"
            build_combined_workbook(workbook_path)

            response = self.client.post(
                "/api/attendance-splitter/scan",
                json={"filePaths": [str(workbook_path)]},
            )

            self.assertEqual(200, response.status_code)
            payload = response.get_json()
            self.assertTrue(payload["success"])
            self.assertEqual([str(workbook_path)], [item["path"] for item in payload["files"]])

    def test_scan_endpoint_rejects_missing_input(self) -> None:
        response = self.client.post("/api/attendance-splitter/scan", json={})

        self.assertEqual(400, response.status_code)
        self.assertFalse(response.get_json()["success"])

    def test_process_endpoint_returns_processor_result(self) -> None:
        processor_result = {
            "success": True,
            "status": "partial",
            "data": {
                "created_count": 1,
                "failed_count": 1,
                "files": [],
            },
        }

        with patch.object(server, "AttendanceSplitter") as splitter_class:
            splitter_class.return_value.process.return_value = processor_result
            response = self.client.post(
                "/api/attendance-splitter/process",
                json={"filePaths": [r"D:\dochazky\combined.xlsx"]},
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual(processor_result, response.get_json())
        splitter_class.return_value.process.assert_called_once()

    def test_process_endpoint_rejects_missing_files(self) -> None:
        response = self.client.post("/api/attendance-splitter/process", json={})

        self.assertEqual(400, response.status_code)
        self.assertFalse(response.get_json()["success"])


if __name__ == "__main__":
    unittest.main()
