from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field, replace
from dvpp_certificates.normalization import (
    normalize_person_name,
    normalize_topic,
    validate_record_date,
)


@dataclass(slots=True)
class RecordOrigin:
    source_mode: str
    source_file: str = ""
    raw_row: str = ""
    model_name: str = ""
    source_index: int = 0


@dataclass(slots=True)
class CertificateRecord:
    surname: str
    name: str
    birth_date: str
    course_name: str
    completion_date: str
    hours: str
    forma: str = ""
    sablona: str = ""
    topic: str = ""
    uncertainty_notes: str = ""
    origin: RecordOrigin | None = None

    def __post_init__(self) -> None:
        required_fields = (
            "surname",
            "name",
            "birth_date",
            "course_name",
            "completion_date",
            "hours",
        )
        for field_name in required_fields:
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            cleaned_value = value.strip()
            if not cleaned_value:
                raise ValueError(f"{field_name} must not be empty")
            setattr(self, field_name, cleaned_value)

        if not isinstance(self.forma, str):
            raise TypeError("forma must be a string")
        if not isinstance(self.sablona, str):
            raise TypeError("sablona must be a string")
        if not isinstance(self.topic, str):
            raise TypeError("topic must be a string")
        if not isinstance(self.uncertainty_notes, str):
            raise TypeError("uncertainty_notes must be a string")
        if self.origin is not None and not isinstance(self.origin, RecordOrigin):
            raise TypeError("origin must be a RecordOrigin instance or None")

        self.surname = normalize_person_name(self.surname, "surname")
        self.name = normalize_person_name(self.name, "name")
        self.birth_date = validate_record_date(self.birth_date, "birth_date")
        self.completion_date = validate_record_date(
            self.completion_date, "completion_date"
        )
        self.forma = self.forma.strip()
        self.sablona = self.sablona.strip()
        self.topic = normalize_topic(self.topic)
        self.uncertainty_notes = self.uncertainty_notes.strip()


@dataclass(slots=True)
class WorkingRecord:
    extracted_record: CertificateRecord
    working_record: CertificateRecord | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.extracted_record, CertificateRecord):
            raise TypeError("extracted_record must be a CertificateRecord")

        extracted_copy = deepcopy(self.extracted_record)
        if self.working_record is None:
            working_copy = deepcopy(extracted_copy)
        else:
            if not isinstance(self.working_record, CertificateRecord):
                raise TypeError("working_record must be a CertificateRecord or None")
            if asdict(self.working_record) != asdict(self.extracted_record):
                raise ValueError(
                    "working_record must match extracted_record at initialization"
                )
            working_copy = deepcopy(self.working_record)

        self.extracted_record = extracted_copy
        self.working_record = working_copy


@dataclass(slots=True)
class ExportMetadata:
    template_path: str = ""
    output_path: str = ""
    project_number: str = ""
    recipient_name: str = ""
    zor_number: str = ""
    fill_header: bool = False


@dataclass(slots=True)
class ExtractionBatch:
    input_mode: str
    records: list[WorkingRecord] = field(default_factory=list)
    source_folder: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    export_metadata: ExportMetadata = field(default_factory=ExportMetadata)
