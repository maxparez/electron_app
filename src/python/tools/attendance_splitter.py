"""Split multi-sheet innovative education attendance workbooks."""

from __future__ import annotations

import logging
import platform
import re
import unicodedata
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


class AttendanceSplitter:
    """Inspect and split workbooks containing multiple attendance sheets."""

    OUTPUT_DIRECTORY_NAME = "rozdelene_dochazky"
    OUTPUT_FILENAME_PREFIX = "dochazka_inovace"
    SUPPORTED_SUFFIXES = {".xlsx"}

    def __init__(self, logger: logging.Logger | None = None, sheet_copier=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.sheet_copier = sheet_copier

    @staticmethod
    def _normalize_cell(value: Any) -> str:
        if value is None:
            return ""
        normalized = unicodedata.normalize("NFKD", str(value))
        without_diacritics = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        return " ".join(without_diacritics.lower().split())

    def _is_attendance_sheet(self, sheet) -> bool:
        b6 = self._normalize_cell(sheet["B6"].value)
        b7 = self._normalize_cell(sheet["B7"].value)
        return "datum aktivity" in b6 and (
            "cas zahajeni" in b7 or "forma vyuky" in b7
        )

    def inspect_workbook(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        result = {
            "path": str(path),
            "name": path.name,
            "eligible": False,
            "attendance_sheets": [],
            "skipped_sheets": [],
        }

        workbook = load_workbook(path, read_only=False, data_only=False, keep_links=True)
        try:
            for sheet in workbook.worksheets:
                if sheet.sheet_state != "visible":
                    result["skipped_sheets"].append(
                        {"sheet_name": sheet.title, "reason": "Skrytý list"}
                    )
                elif self._is_attendance_sheet(sheet):
                    result["attendance_sheets"].append(sheet.title)
                else:
                    result["skipped_sheets"].append(
                        {
                            "sheet_name": sheet.title,
                            "reason": "List neodpovídá formátu docházky",
                        }
                    )
        finally:
            workbook.close()

        result["eligible"] = len(result["attendance_sheets"]) >= 2
        return result

    def scan_folder(self, folder_path: str | Path) -> list[dict[str, Any]]:
        folder = Path(folder_path)
        matches = []

        for path in sorted(folder.iterdir(), key=lambda item: item.name.lower()):
            if (
                not path.is_file()
                or path.name.startswith("~$")
                or path.suffix.lower() not in self.SUPPORTED_SUFFIXES
            ):
                continue

            try:
                inspection = self.inspect_workbook(path)
            except Exception as exc:
                self.logger.warning("Cannot inspect workbook %s: %s", path, exc)
                continue

            if inspection["eligible"]:
                matches.append(inspection)

        return matches

    def normalize_sheet_name(self, sheet_name: str) -> str:
        normalized = unicodedata.normalize("NFKD", sheet_name)
        without_diacritics = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", without_diacritics)
        safe_name = safe_name.strip("_").lower()
        return safe_name or "list"

    def build_output_path(self, output_dir: str | Path, sheet_name: str) -> Path:
        folder = Path(output_dir)
        normalized_name = self.normalize_sheet_name(sheet_name)
        base_name = f"{self.OUTPUT_FILENAME_PREFIX}_{normalized_name}"
        candidate = folder / f"{base_name}.xlsx"
        suffix = 2

        while candidate.exists():
            candidate = folder / f"{base_name}_{suffix}.xlsx"
            suffix += 1

        return candidate

    def process(
        self,
        files: list[str | Path],
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del options
        file_results = []
        created_count = 0
        failed_count = 0

        for file_path in files:
            source_path = Path(file_path)
            file_result = {
                "source": str(source_path),
                "output_dir": str(source_path.parent / self.OUTPUT_DIRECTORY_NAME),
                "status": "error",
                "created_files": [],
                "skipped_sheets": [],
                "errors": [],
            }

            try:
                inspection = self.inspect_workbook(source_path)
                file_result["skipped_sheets"] = inspection["skipped_sheets"]
            except Exception as exc:
                file_result["errors"].append(f"Soubor nelze načíst: {exc}")
                failed_count += 1
                file_results.append(file_result)
                continue

            if not inspection["eligible"]:
                file_result["errors"].append(
                    "Soubor neobsahuje alespoň dva vhodné listy docházky"
                )
                failed_count += 1
                file_results.append(file_result)
                continue

            output_dir = Path(file_result["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)

            for sheet_name in inspection["attendance_sheets"]:
                output_path = self.build_output_path(output_dir, sheet_name)
                try:
                    self._copy_sheet(source_path, sheet_name, output_path)
                    file_result["created_files"].append(
                        {
                            "sheet_name": sheet_name,
                            "path": str(output_path),
                            "filename": output_path.name,
                        }
                    )
                    created_count += 1
                except Exception as exc:
                    if output_path.exists():
                        output_path.unlink()
                    file_result["errors"].append(f"{sheet_name}: {exc}")
                    failed_count += 1

            if file_result["created_files"] and file_result["errors"]:
                file_result["status"] = "partial"
            elif file_result["created_files"]:
                file_result["status"] = "success"

            file_results.append(file_result)

        if created_count and failed_count:
            status = "partial"
        elif created_count:
            status = "success"
        else:
            status = "error"

        return {
            "success": created_count > 0,
            "status": status,
            "data": {
                "files": file_results,
                "created_count": created_count,
                "failed_count": failed_count,
            },
        }

    def _copy_sheet(
        self,
        source_path: Path,
        sheet_name: str,
        output_path: Path,
    ) -> None:
        if self.sheet_copier is not None:
            self.sheet_copier(source_path, sheet_name, output_path)
            return

        self._copy_sheet_with_xlwings(source_path, sheet_name, output_path)

    @staticmethod
    def _copy_sheet_with_xlwings(
        source_path: Path,
        sheet_name: str,
        output_path: Path,
    ) -> None:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Rozdělení listů vyžaduje Windows s nainstalovaným Microsoft Excelem"
            )

        try:
            import xlwings as xw
        except ImportError as exc:
            raise RuntimeError("Knihovna xlwings není dostupná") from exc

        app = None
        source_book = None
        output_book = None
        try:
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            source_book = app.books.open(
                str(source_path.resolve()),
                update_links=False,
                read_only=True,
            )
            source_book.sheets[sheet_name].api.Copy()
            output_book = app.books.active
            output_book.save(str(output_path.resolve()))
        finally:
            if output_book is not None:
                output_book.close()
            if source_book is not None:
                source_book.close()
            if app is not None:
                app.quit()
