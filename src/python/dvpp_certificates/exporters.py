from __future__ import annotations

import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from dvpp_certificates.domain import CertificateRecord, ExportMetadata, RecordOrigin, WorkingRecord


DEFAULT_EXCEL_TEMPLATE_PATH = (
    r"D:\JAK2024\Dokumenty\Evidence_podpor_poskytnutych_ucastnikum_vzdelavani_MS_ZS_upravene_DVPP.xlsx"
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
        payload.get("sablona", ""),
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
        sheet = book.sheets["podpory"]
        _write_records_to_sheet(sheet, records, export_metadata)
        book.save()
    finally:
        if book is not None:
            book.close()
        app.quit()


def _write_records_to_sheet(
    sheet,
    records: list[CertificateRecord],
    export_metadata: ExportMetadata,
) -> None:
    was_protected = bool(getattr(getattr(sheet, "api", None), "ProtectContents", False))

    try:
        if was_protected:
            sheet.api.Unprotect()

        if export_metadata.fill_header:
            sheet.range("D6").value = export_metadata.project_number
            sheet.range("I6").value = export_metadata.zor_number
            sheet.range("D7").value = export_metadata.recipient_name

        data_start_row = 11
        data_end_row = max(data_start_row + len(records) - 1, 500)
        sheet.range(f"B{data_start_row}:J{data_end_row}").clear_contents()

        if records:
            sheet.range(f"B{data_start_row}").value = [
                [
                    record.surname,
                    record.name,
                    record.sablona,
                    record.course_name,
                    record.completion_date,
                    record.hours,
                    "",
                    record.topic,
                    "",
                ]
                for record in records
            ]
    finally:
        if was_protected:
            sheet.api.Protect()
