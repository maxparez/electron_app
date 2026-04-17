#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime
from typing import Mapping
import re


TOPIC_WHITELIST = {
    "umela inteligence",
}

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


def normalize_date(value: str) -> str:
    stripped = value.strip()
    for date_format in _DATE_FORMATS:
        try:
            parsed_date = datetime.strptime(stripped, date_format)
        except ValueError:
            continue
        return parsed_date.strftime("%d.%m.%Y")
    return stripped


def normalize_topic(value: str) -> str:
    stripped = value.strip()
    if stripped in TOPIC_WHITELIST:
        return stripped
    return ""


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
