#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping
import re


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
    (
        "vzdelavani deti/zaku cizincu a deti/zaku s potrebou jazykove podpory"
    ),
    "rozvoj pedagogickych kompetenci v oblasti metod a forem vzdelavani",
    "komunikace se zakonnymi zastupci",
    "management skol",
    "rizeni organizace",
    "leadership a rizeni pedagogickeho procesu",
    "vzdelavani deti a zaku z marginalizovanych skupin, jako jsou Romove",
    "podpora uvadejicich/provazejicich ucitelu",
)

TOPIC_WHITELIST = frozenset(TOPIC_CATALOG)

_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%d/%m/%Y",
)

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

        self.surname = _normalize_person_name(self.surname, "surname")
        self.name = _normalize_person_name(self.name, "name")
        self.birth_date = _validate_record_date(self.birth_date, "birth_date")
        self.completion_date = _validate_record_date(
            self.completion_date, "completion_date"
        )
        self.topic = normalize_topic(self.topic)
        self.uncertainty_notes = self.uncertainty_notes.strip()


@dataclass(slots=True)
class ExtractionResult:
    certificates: list[CertificateRecord]

    def __post_init__(self) -> None:
        if not isinstance(self.certificates, list):
            raise TypeError("certificates must be a list")
        for certificate in self.certificates:
            if not isinstance(certificate, CertificateRecord):
                raise TypeError("certificates must contain CertificateRecord items")


def strip_titles(value: str) -> str:
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
    cleaned = strip_titles(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def normalize_date(value: str) -> str:
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

    normalized = normalize_date(date_value)
    if not _NORMALIZED_DATE_RE.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date")
    try:
        datetime.strptime(normalized, "%d.%m.%Y")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid dd.mm.yyyy date") from exc
    if has_uncertainty_marker:
        return f"{normalized}?"
    return normalized


def normalize_topic(value: str) -> str:
    stripped = value.strip()
    if stripped in TOPIC_WHITELIST:
        return stripped
    return ""


def build_extraction_prompt() -> str:
    topic_catalog = ", ".join(TOPIC_CATALOG)
    return f"""
### ROLE A CIL ###
Jsi "Certifikator v2.1", ultra-presny AI asistent specializovany na OCR extrakci dat z certifikatu a osvedceni o dalsim vzdelavani pedagogickych pracovniku (DVPP).

### KLICOVY KONTEXT A ZNALOSTI ###
* Jsi expert na terminologii v oblasti ceskeho skolstvi a DVPP.
* Rozumis kontextu ceskych jmen a prijmeni a jejich sklonovani.
* Prirazeni kategorie "Tema" se ridi vyhradne nasledujicim zavaznym ciselnikem. Musis dodrzet presne zneni a mala pismena.

**ZAVAZNY CISELNIK TEMAT:**
* {topic_catalog}

### OMEZENI, PRAVIDLA A LOGIKA ZPRACOVANI ###
* Pokud si jakymkoli udajem (jmeno, datum, cislo) nejsi jisty na 100 % kvuli spatne kvalite skenu, pripoj za nej otaznik.
* Pole "Tema" vyplnuj pouze a vyhradne hodnotou ze zavazneho ciselniku temat.
* Pole "Datum ukonceni vzdelavani" je vzdy termin konani vzdelavani. Pokud je vzdelavani vice dnu, pak je to nejvyssi datum.
* Vzdy dodrz strukturu poli:
Prijmeni<TAB>Jmeno<TAB>Datum narozeni<TAB>Nazev kurzu<TAB>Datum ukonceni vzdelavani<TAB>Pocet hodin<TAB><TAB>Tema
* Datum narozeni musi byt vzdy ve tvaru dd.mm.yyyy.
* Datum ukonceni vzdelavani musi byt vzdy ve tvaru dd.mm.yyyy.
""".strip()


def format_tsv_row(record: Mapping[str, str]) -> str:
    fields = [
        record.get("surname", ""),
        record.get("name", ""),
        record.get("birth_date", ""),
        record.get("course_name", ""),
        record.get("completion_date", ""),
        record.get("hours", ""),
        "",
        record.get("topic", ""),
    ]
    return "\t".join(str(field) for field in fields)
