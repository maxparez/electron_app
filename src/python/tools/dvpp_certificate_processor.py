from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from dvpp_cert_extraction import collect_input_files, validate_input_file
from dvpp_certificates.domain import ExtractionBatch, RecordOrigin, WorkingRecord
from dvpp_certificates.exporters import export_records_to_excel, export_records_to_tsv
from dvpp_certificates.importers import GeminiCertificateImporter
from dvpp_certificates.normalization import normalize_certificate_fields
from dvpp_certificates.raw_text_parser import parse_raw_text_batch

from .base_tool import BaseTool


class DvppCertificateProcessor(BaseTool):
    def __init__(self, logger=None, importer: GeminiCertificateImporter | None = None):
        super().__init__(logger)
        self.importer = importer or GeminiCertificateImporter()

    def validate_inputs(self, files: List[str], options: Dict[str, Any]) -> bool:
        self.clear_messages()

        folder_path = options.get("folder_path")
        model_name = options.get("model_name")

        if not folder_path:
            self.add_error("Nebyla zadána složka s certifikáty")
            return False

        folder = Path(str(folder_path)).expanduser()
        if not folder.exists() or not folder.is_dir():
            self.add_error(f"Složka s certifikáty neexistuje: {folder_path}")
            return False

        if not model_name:
            self.add_error("Nebyl zvolen Gemini model")
            return False

        try:
            if files:
                for file_path in files:
                    validate_input_file(file_path)
            else:
                collect_input_files(folder)
        except Exception as exc:
            self.add_error(str(exc))
            return False

        return True

    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_inputs(files, options):
            return self.get_result(False)

        folder_path = str(Path(str(options["folder_path"])).expanduser())
        model_name = str(options["model_name"])
        api_key = options.get("api_key")
        resolved_files = self._resolve_files(files, folder_path)

        batch = ExtractionBatch(input_mode="gemini", source_folder=folder_path)
        diagnostics: list[dict[str, Any]] = []

        for file_path in resolved_files:
            try:
                result = self.importer.import_file(
                    file_path,
                    model_name=model_name,
                    api_key=api_key,
                )
                for index, certificate in enumerate(result.certificates, start=1):
                    origin = RecordOrigin(
                        source_mode="gemini",
                        source_file=file_path,
                        model_name=model_name,
                        source_index=index,
                    )
                    normalized = normalize_certificate_fields(
                        asdict(certificate),
                        origin=origin,
                    )
                    batch.records.append(WorkingRecord(extracted_record=normalized))

                diagnostics.append(
                    {
                        "source_file": file_path,
                        "success": True,
                        "record_count": len(result.certificates),
                        "warnings": [],
                        "errors": [],
                    }
                )
            except Exception as exc:
                error_message = str(exc)
                batch.errors.append(f"{Path(file_path).name}: {error_message}")
                diagnostics.append(
                    {
                        "source_file": file_path,
                        "success": False,
                        "record_count": 0,
                        "warnings": [],
                        "errors": [error_message],
                    }
                )

        successful_files = sum(1 for item in diagnostics if item["success"])
        failed_files = len(diagnostics) - successful_files

        if failed_files:
            self.add_warning(
                f"Nepodařilo se zpracovat {failed_files} z {len(diagnostics)} souborů"
            )

        batch.warnings.extend(self.warnings)

        data = {
            "batch": self._serialize_batch(batch),
            "diagnostics": diagnostics,
            "processedFiles": len(diagnostics),
            "successfulFiles": successful_files,
            "failedFiles": failed_files,
            "modelName": model_name,
        }

        if not batch.records:
            self.add_error("Nepodařilo se vytěžit žádné certifikáty")
            batch.errors = self.errors.copy() + [
                error for error in batch.errors if error not in self.errors
            ]
            data["batch"] = self._serialize_batch(batch)
            return self.get_result(False, data)

        return self.get_result(True, data)

    def _resolve_files(self, files: List[str], folder_path: str) -> list[str]:
        if files:
            return [str(validate_input_file(file_path)) for file_path in files]
        return [str(path) for path in collect_input_files(folder_path)]

    def _serialize_batch(self, batch: ExtractionBatch) -> dict[str, Any]:
        return {
            "input_mode": batch.input_mode,
            "source_folder": batch.source_folder,
            "records": [
                {
                    "extracted_record": asdict(record.extracted_record),
                    "working_record": asdict(record.working_record),
                }
                for record in batch.records
            ],
            "warnings": batch.warnings.copy(),
            "errors": batch.errors.copy(),
            "export_metadata": asdict(batch.export_metadata),
        }

    def export_tsv(
        self,
        records_payload: list[dict[str, Any]],
        *,
        output_path: str | None = None,
    ) -> Dict[str, Any]:
        self.clear_messages()
        try:
            data = export_records_to_tsv(records_payload, output_path=output_path)
            return self.get_result(True, data)
        except Exception as exc:
            self.add_error(str(exc))
            return self.get_result(False)

    def export_excel(
        self,
        records_payload: list[dict[str, Any]],
        export_metadata_payload: dict[str, Any],
        *,
        template_path: str | None = None,
        output_path: str | None = None,
    ) -> Dict[str, Any]:
        self.clear_messages()
        try:
            exported_path = export_records_to_excel(
                records_payload,
                export_metadata_payload,
                template_path=template_path,
                output_path=output_path,
            )
            return self.get_result(
                True,
                {
                    "output_path": exported_path,
                    "template_path": template_path,
                },
            )
        except Exception as exc:
            self.add_error(str(exc))
            return self.get_result(False)

    def import_raw_text(self, raw_text: str) -> Dict[str, Any]:
        self.clear_messages()
        try:
            batch = parse_raw_text_batch(raw_text)
            return self.get_result(
                True,
                {
                    "batch": self._serialize_batch(batch),
                    "processedRows": len(batch.records),
                },
            )
        except Exception as exc:
            self.add_error(str(exc))
            return self.get_result(False)
