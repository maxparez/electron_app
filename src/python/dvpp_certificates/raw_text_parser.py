from __future__ import annotations

from dvpp_certificates.domain import ExtractionBatch, RecordOrigin, WorkingRecord
from dvpp_certificates.normalization import normalize_certificate_fields


LEGACY_COLUMN_COUNT = 8
CURRENT_COLUMN_COUNT = 9


def parse_raw_text_batch(text: str) -> ExtractionBatch:
    records: list[WorkingRecord] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue

        columns = line.split("\t")
        if len(columns) not in (LEGACY_COLUMN_COUNT, CURRENT_COLUMN_COUNT):
            raise ValueError(
                "Malformed raw text row at line "
                f"{line_number}: wrong column count, expected 8 or 9 tab-separated columns"
            )

        if len(columns) == CURRENT_COLUMN_COUNT:
            sablona = columns[3]
            course_name = columns[4]
            completion_date = columns[5]
            hours = columns[6]
            forma = columns[7]
            topic = columns[8]
        else:
            sablona = ""
            course_name = columns[3]
            completion_date = columns[4]
            hours = columns[5]
            forma = columns[6]
            topic = columns[7]

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
                "sablona": sablona,
                "course_name": course_name,
                "completion_date": completion_date,
                "hours": hours,
                "forma": forma,
                "topic": topic,
            },
            origin=origin,
        )
        records.append(WorkingRecord(extracted_record=record))

    if not records:
        raise ValueError("No certificate rows found in raw text input")

    return ExtractionBatch(input_mode="raw_text", records=records)
