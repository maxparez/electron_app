from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
import re


_TOPIC_CATALOG = (
    "pedagogicka diagnostika",
    "individualizace vzdelavani",
    "formativni hodnoceni",
    "podpora nadani/talentu",
    "recova vychova",
    "grafomotorika",
    "rozvoj gramotnosti",
    "rozvoj digitalnich kompetenci",
    "podpora polytechniky",
    (
        "vzdelavani pro udrzitelny rozvoj - napr. EVVO "
        "(environmentalni vzdelavani, vychova a osveta), klimaticke vzdelavani, "
        "principy mistne zakotveneho uceni"
    ),
    "well-being a psychohygiena",
    "genderova tematika v obsahu vzdelavani",
    "vyuka modernich dejin",
    "medialni gramotnost",
    "prevence kybersikany",
    "chovani na socialnich sitich",
    "umela inteligence",
    "pohybove aktivity",
    (
        "prace s detmi/zaky se specialnimi vzdelavacimi potrebami; "
        "vzdelavani heterogennich kolektivu"
    ),
    "vzdelavani deti/zaku cizincu a deti/zaku s potrebou jazykove podpory",
    "rozvoj pedagogickych kompetenci v oblasti metod a forem vzdelavani",
    "komunikace se zakonnymi zastupci",
    "management skol",
    "rizeni organizace",
    "leadership a rizeni pedagogickeho procesu",
    "vzdelavani deti a zaku z marginalizovanych skupin, jako jsou Romove",
    "podpora uvadejicich/provazejicich ucitelu",
)
_TOPIC_WHITELIST = frozenset(_TOPIC_CATALOG)
_DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")
_TITLE_PATTERNS = (
    r"Bc\.",
    r"Mgr\.",
    r"Ing\.",
    r"RNDr\.",
    r"JUDr\.",
    r"MUDr\.",
    r"PhDr\.",
    r"Ph\.D\.",
    r"DiS\.",
)
_LEADING_TITLES_RE = re.compile(rf"^(?:{'|'.join(_TITLE_PATTERNS)})\s*")
_TRAILING_TITLES_RE = re.compile(rf"\s*,?\s*(?:{'|'.join(_TITLE_PATTERNS)})$")
_NORMALIZED_DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def _strip_titles(value: str) -> str:
    cleaned = value.strip()
    while cleaned:
        updated = _LEADING_TITLES_RE.sub("", cleaned).strip(" ,")
        if updated == cleaned:
            break
        cleaned = updated

    while cleaned:
        updated = _TRAILING_TITLES_RE.sub("", cleaned).strip(" ,")
        if updated == cleaned:
            break
        cleaned = updated

    return cleaned


def _normalize_person_name(value: str, field_name: str) -> str:
    cleaned = _strip_titles(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _normalize_date(value: str) -> str:
    stripped = value.strip()
    for date_format in _DATE_FORMATS:
        try:
            parsed_date = datetime.strptime(stripped, date_format)
        except ValueError:
            continue
        return parsed_date.strftime("%d.%m.%Y")
    return stripped


def _validate_record_date(value: str, field_name: str) -> str:
    stripped = value.strip()
    has_uncertainty_marker = stripped.endswith("?")
    date_value = stripped[:-1].strip() if has_uncertainty_marker else stripped

    normalized = _normalize_date(date_value)
    if not _NORMALIZED_DATE_RE.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date")
    try:
        datetime.strptime(normalized, "%d.%m.%Y")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date") from exc
    if has_uncertainty_marker:
        return f"{normalized}?"
    return normalized


def _normalize_topic(value: str) -> str:
    stripped = value.strip()
    if stripped in _TOPIC_WHITELIST:
        return stripped
    return ""


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

        if not isinstance(self.topic, str):
            raise TypeError("topic must be a string")
        if not isinstance(self.uncertainty_notes, str):
            raise TypeError("uncertainty_notes must be a string")
        if self.origin is not None and not isinstance(self.origin, RecordOrigin):
            raise TypeError("origin must be a RecordOrigin instance or None")

        self.surname = _normalize_person_name(self.surname, "surname")
        self.name = _normalize_person_name(self.name, "name")
        self.birth_date = _validate_record_date(self.birth_date, "birth_date")
        self.completion_date = _validate_record_date(
            self.completion_date, "completion_date"
        )
        self.topic = _normalize_topic(self.topic)
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
    sablona: str = ""
    forma: str = ""
    qualification_split: str = ""


@dataclass(slots=True)
class ExtractionBatch:
    input_mode: str
    records: list[WorkingRecord] = field(default_factory=list)
    source_folder: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    export_metadata: ExportMetadata = field(default_factory=ExportMetadata)
