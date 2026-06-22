#!/usr/bin/env python3
"""Regression tests for innovative education student name extraction."""

import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from openpyxl import Workbook

from src.python.tools.inv_vzd_processor import InvVzdProcessor


SHEET_XML_NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def create_workbook_without_sheet_dimension(path: Path) -> None:
    """Create an attendance workbook whose worksheet XML has no dimension element."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "zdroj-dochazka"
    sheet["B12"] = "Bledý Ladislav"
    sheet["B13"] = "Burešová Katrin"
    sheet["B14"] = "Cínová Tiara"
    workbook.save(path)

    rewritten_path = path.with_suffix(".rewritten.xlsx")
    with zipfile.ZipFile(path, "r") as source_zip:
        with zipfile.ZipFile(rewritten_path, "w", zipfile.ZIP_DEFLATED) as target_zip:
            for item in source_zip.infolist():
                data = source_zip.read(item.filename)
                if item.filename == "xl/worksheets/sheet1.xml":
                    root = ET.fromstring(data)
                    dimension = root.find(f"{SHEET_XML_NAMESPACE}dimension")
                    if dimension is not None:
                        root.remove(dimension)
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                target_zip.writestr(item, data)

    rewritten_path.replace(path)


class InvVzdStudentNameExtractionTests(unittest.TestCase):
    def test_extract_student_names_handles_read_only_worksheet_without_dimension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_file = Path(temp_dir) / "attendance.xlsx"
            create_workbook_without_sheet_dimension(source_file)

            processor = InvVzdProcessor()
            processor.version = "16"

            student_names = processor._extract_student_names_from_data(str(source_file))

            self.assertEqual(
                ["Bledý Ladislav", "Burešová Katrin", "Cínová Tiara"],
                student_names,
            )
            self.assertEqual([], processor.errors)


if __name__ == "__main__":
    unittest.main()
