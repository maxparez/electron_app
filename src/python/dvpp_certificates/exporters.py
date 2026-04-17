from __future__ import annotations

import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from dvpp_certificates.domain import CertificateRecord, ExportMetadata, RecordOrigin, WorkingRecord


DEFAULT_EXCEL_TEMPLATE_PATH = (
    r"D:\JAK2024\Dokumenty\Evidence_podpor_poskytnutych_ucastnikum_vzdelavani_MS_ZS_upravene_DVPP.xlsx"
)
REQUIRED_EXPORT_METADATA_FIELDS = (
    "project_number",
    "recipient_name",
    "zor_number",
    "sablona",
    "forma",
)


def resolve_excel_template_path(template_path: str | None) -> str:
    return template_path or DEFAULT_EXCEL_TEMPLATE_PATH


def export_records_to_tsv(
    records: list[WorkingRecord | Mapping[str, Any]],
    *,
    output_path: str | None = None,
) -> dict[str, str | None]:
    lines = [_format_tsv_row(_coerce_working_record(record)) for record in records]
    content = "\n".join(lines)

    if output_path:
        Path(output_path).expanduser().write_text(content, encoding="utf-8")

    return {
        "content": content,
        "output_path": output_path,
    }


def export_records_to_excel(
    records: list[WorkingRecord | Mapping[str, Any]],
    export_metadata: ExportMetadata | Mapping[str, Any],
    *,
    template_path: str | None = None,
    output_path: str | None = None,
    workbook_writer=None,
) -> str:
    metadata = _coerce_export_metadata(export_metadata)
    _validate_export_metadata(metadata)

    resolved_template = Path(resolve_excel_template_path(template_path)).expanduser()
    if not resolved_template.exists() or not resolved_template.is_file():
        raise FileNotFoundError(f"Excel template not found: {resolved_template}")

    resolved_output = _resolve_excel_output_path(resolved_template, output_path)
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(resolved_template, resolved_output)

    records_to_export = [_coerce_working_record(record) for record in records]
    writer = _write_records_with_xlwings if workbook_writer is None else workbook_writer
    writer(str(resolved_output), records_to_export, metadata)
    return str(resolved_output)


def _resolve_excel_output_path(template_path: Path, output_path: str | None) -> Path:
    if output_path:
        return Path(output_path).expanduser()
    return template_path.with_name(f"{template_path.stem}_dvpp_certificates.xlsx")


def _coerce_export_metadata(
    export_metadata: ExportMetadata | Mapping[str, Any],
) -> ExportMetadata:
    if isinstance(export_metadata, ExportMetadata):
        return export_metadata
    if not isinstance(export_metadata, Mapping):
        raise TypeError("export_metadata must be an ExportMetadata or mapping")
    return ExportMetadata(**dict(export_metadata))


def _validate_export_metadata(export_metadata: ExportMetadata) -> None:
    for field_name in REQUIRED_EXPORT_METADATA_FIELDS:
        value = getattr(export_metadata, field_name, "")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing required export metadata: {field_name}")


def _coerce_working_record(record: WorkingRecord | Mapping[str, Any]) -> CertificateRecord:
    if isinstance(record, WorkingRecord):
        return record.working_record
    if not isinstance(record, Mapping):
        raise TypeError("record must be a WorkingRecord or mapping")

    payload = dict(record.get("working_record", record))
    origin_payload = payload.get("origin")
    if isinstance(origin_payload, Mapping):
        payload["origin"] = RecordOrigin(**dict(origin_payload))
    return CertificateRecord(**payload)


def _format_tsv_row(record: CertificateRecord) -> str:
    payload = asdict(record)
    fields = [
        payload.get("surname", ""),
        payload.get("name", ""),
        payload.get("birth_date", ""),
        payload.get("course_name", ""),
        payload.get("completion_date", ""),
        payload.get("hours", ""),
        "",
        payload.get("topic", ""),
    ]
    return "\t".join(str(field) for field in fields)


def _write_records_with_xlwings(
    output_path: str,
    records: list[CertificateRecord],
    export_metadata: ExportMetadata,
) -> None:
    import xlwings as xw

    app = xw.App(visible=False, add_book=False)
    book = None
    try:
        book = app.books.open(output_path)
        sheet_name = "DVPP_CERT_IMPORT"
        try:
            sheet = book.sheets[sheet_name]
            sheet.clear()
        except Exception:
            sheet = book.sheets.add(sheet_name, after=book.sheets[-1])

        sheet.range("A1").value = [
            ["Project number", export_metadata.project_number],
            ["Recipient", export_metadata.recipient_name],
            ["ZoR number", export_metadata.zor_number],
            ["Sablona", export_metadata.sablona],
            ["Forma", export_metadata.forma],
            ["Qualification split", export_metadata.qualification_split],
        ]
        sheet.range("A8").value = [
            "Prijmeni",
            "Jmeno",
            "Datum narozeni",
            "Nazev kurzu",
            "Datum ukonceni vzdelavani",
            "Pocet hodin",
            "Tema",
        ]
        if records:
            sheet.range("A9").value = [
                [
                    record.surname,
                    record.name,
                    record.birth_date,
                    record.course_name,
                    record.completion_date,
                    record.hours,
                    record.topic,
                ]
                for record in records
            ]
        book.save()
    finally:
        if book is not None:
            book.close()
        app.quit()
