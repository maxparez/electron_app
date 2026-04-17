from __future__ import annotations

from dvpp_certificates.domain import ExtractionBatch, RecordOrigin, WorkingRecord
from dvpp_certificates.normalization import normalize_certificate_fields


EXPECTED_COLUMN_COUNT = 8


def parse_raw_text_batch(text: str) -> ExtractionBatch:
    records: list[WorkingRecord] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        columns = line.split("\t")
        if len(columns) != EXPECTED_COLUMN_COUNT:
            raise ValueError(
                "Malformed raw text row at line "
                f"{line_number}: wrong column count, expected 8 tab-separated columns"
            )
        if columns[6] != "":
            raise ValueError(
                f"Malformed raw text row at line {line_number}: spacer column must be empty"
            )

        origin = RecordOrigin(
            source_mode="raw_text",
            raw_row=line,
            source_index=len(records) + 1,
        )
        record = normalize_certificate_fields(
            {
                "surname": columns[0],
                "name": columns[1],
                "birth_date": columns[2],
                "course_name": columns[3],
                "completion_date": columns[4],
                "hours": columns[5],
                "topic": columns[7],
            },
            origin=origin,
        )
        records.append(WorkingRecord(extracted_record=record))

    if not records:
        raise ValueError("No certificate rows found in raw text input")

    return ExtractionBatch(input_mode="raw_text", records=records)
