from __future__ import annotations

from datetime import datetime
import re
from typing import TYPE_CHECKING, Mapping
import unicodedata

if TYPE_CHECKING:
    from dvpp_certificates.domain import RecordOrigin


TOPIC_CATALOG = (
    "pedagogická diagnostika",
    "individualizace vzdělávání",
    "formativní hodnocení",
    "podpora nadání/talentu",
    "řečová výchova",
    "grafomotorika",
    "rozvoj gramotností",
    "rozvoj digitálních kompetencí",
    "podpora polytechniky",
    (
        "vzdělávání pro udržitelný rozvoj – např. EVVO "
        "(environmentální vzdělávání, výchova a osvěta), klimatické vzdělávání, "
        "principy místně zakotveného učení"
    ),
    "well-being a psychohygiena",
    "genderová tematika v obsahu vzdělávání",
    "výuka moderních dějin",
    "mediální gramotnost",
    "prevence kyberšikany",
    "chování na sociálních sítích",
    "umělá inteligence",
    "pohybové aktivity",
    (
        "práce s dětmi/žáky se speciálními vzdělávacími potřebami; "
        "vzdělávání heterogenních kolektivů"
    ),
    "vzdělávání dětí/žáků cizinců a dětí/žáků s potřebou jazykové podpory",
    "rozvoj pedagogických kompetencí v oblasti metod a forem vzdělávání",
    "komunikace se zákonnými zástupci",
    "management škol",
    "řízení organizace",
    "leadership a řízení pedagogického procesu",
    "vzdělávání dětí a žáků z marginalizovaných skupin, jako jsou Romové",
    "podpora uvádějících/provázejících učitelů",
)
TOPIC_WHITELIST = frozenset(TOPIC_CATALOG)
TOPIC_LOOKUP = {}
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


def _normalize_topic_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    without_diacritics = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    ascii_dash = without_diacritics.replace("–", "-").replace("—", "-")
    collapsed = re.sub(r"\s+", " ", ascii_dash)
    return collapsed.strip()


for topic_name in TOPIC_CATALOG:
    TOPIC_LOOKUP[_normalize_topic_key(topic_name)] = topic_name


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
    if not stripped:
        return ""
    return TOPIC_LOOKUP.get(_normalize_topic_key(stripped), "")


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
        "forma": _optional_string_field(raw_record, "forma"),
        "sablona": _optional_string_field(raw_record, "sablona"),
        "topic": _optional_string_field(raw_record, "topic"),
        "uncertainty_notes": _optional_string_field(raw_record, "uncertainty_notes"),
        "origin": origin,
    }
    return CertificateRecord(**payload)
