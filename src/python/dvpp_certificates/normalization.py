from __future__ import annotations

from datetime import datetime
import re
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from dvpp_certificates.domain import RecordOrigin


TOPIC_CATALOG = (
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
TOPIC_WHITELIST = frozenset(TOPIC_CATALOG)
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")
TITLE_PATTERNS = (
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
LEADING_TITLES_RE = re.compile(rf"^(?:{'|'.join(TITLE_PATTERNS)})\s*")
TRAILING_TITLES_RE = re.compile(rf"\s*,?\s*(?:{'|'.join(TITLE_PATTERNS)})$")
NORMALIZED_DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def strip_titles(value: str) -> str:
    cleaned = value.strip()
    while cleaned:
        updated = LEADING_TITLES_RE.sub("", cleaned).strip(" ,")
        if updated == cleaned:
            break
        cleaned = updated

    while cleaned:
        updated = TRAILING_TITLES_RE.sub("", cleaned).strip(" ,")
        if updated == cleaned:
            break
        cleaned = updated

    return cleaned


def normalize_person_name(value: str, field_name: str) -> str:
    cleaned = strip_titles(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def normalize_date(value: str) -> str:
    stripped = value.strip()
    has_uncertainty_marker = stripped.endswith("?")
    date_value = stripped[:-1].strip() if has_uncertainty_marker else stripped

    normalized = date_value
    for date_format in DATE_FORMATS:
        try:
            parsed_date = datetime.strptime(date_value, date_format)
        except ValueError:
            continue
        normalized = parsed_date.strftime("%d.%m.%Y")
        break

    if has_uncertainty_marker:
        return f"{normalized}?"
    return normalized


def validate_record_date(value: str, field_name: str) -> str:
    normalized = normalize_date(value)
    date_value = normalized[:-1] if normalized.endswith("?") else normalized
    if not NORMALIZED_DATE_RE.fullmatch(date_value):
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date")
    try:
        datetime.strptime(date_value, "%d.%m.%Y")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date") from exc
    return normalized


def normalize_topic(value: str) -> str:
    stripped = value.strip()
    if stripped in TOPIC_WHITELIST:
        return stripped
    return ""


def _require_string_field(raw_record: Mapping[str, object], field_name: str) -> str:
    if field_name not in raw_record:
        raise TypeError(f"Missing required field: {field_name}")
    value = raw_record[field_name]
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _optional_string_field(raw_record: Mapping[str, object], field_name: str) -> str:
    value = raw_record.get(field_name, "")
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def normalize_certificate_fields(
    raw_record: Mapping[str, object],
    origin: RecordOrigin | None = None,
):
    from dvpp_certificates.domain import CertificateRecord

    payload = {
        "surname": _require_string_field(raw_record, "surname"),
        "name": _require_string_field(raw_record, "name"),
        "birth_date": _require_string_field(raw_record, "birth_date"),
        "course_name": _require_string_field(raw_record, "course_name"),
        "completion_date": _require_string_field(raw_record, "completion_date"),
        "hours": _require_string_field(raw_record, "hours"),
        "topic": _optional_string_field(raw_record, "topic"),
        "uncertainty_notes": _optional_string_field(raw_record, "uncertainty_notes"),
        "origin": origin,
    }
    return CertificateRecord(**payload)
