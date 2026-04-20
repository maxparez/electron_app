from __future__ import annotations

from pathlib import Path


def classify_include_paths(root_dir: str | Path, include_paths: list[str]) -> tuple[list[str], list[str]]:
    root = Path(root_dir)
    file_entries: list[str] = []
    directory_entries: list[str] = []

    for entry in include_paths:
        candidate = root / entry
        if candidate.is_dir():
            directory_entries.append(entry.rstrip("/"))
        else:
            file_entries.append(entry)

    return sorted(file_entries), sorted(directory_entries)
