#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Callable, Mapping

from dvpp_certificates.domain import CertificateRecord
from dvpp_certificates.normalization import (
    TOPIC_CATALOG,
    normalize_certificate_fields,
    normalize_date,
    normalize_topic,
    strip_titles,
)


SUPPORTED_EXTENSIONS = frozenset({".pdf", ".jpg", ".jpeg", ".png"})
SUPPORTED_MODELS = (
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
)
MODEL_NAME_MAPPING = {
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
}
PRIMARY_API_KEY_ENV = "GEMINI_API_KEY"
FALLBACK_API_KEY_ENV = "GOOGLE_API_KEY"

@dataclass(slots=True)
class ExtractionResult:
    certificates: list[CertificateRecord]

    def __post_init__(self) -> None:
        if not isinstance(self.certificates, list):
            raise TypeError("certificates must be a list")
        for certificate in self.certificates:
            if not isinstance(certificate, CertificateRecord):
                raise TypeError("certificates must contain CertificateRecord items")

def resolve_model_name(model_name: str) -> str:
    try:
        return MODEL_NAME_MAPPING[model_name]
    except KeyError as exc:
        supported = ", ".join(SUPPORTED_MODELS)
        raise ValueError(f"Unsupported model: {model_name}. Supported: {supported}") from exc


def load_api_key(env: Mapping[str, str] | None = None) -> str:
    source_env = os.environ if env is None else env
    api_key = source_env.get(PRIMARY_API_KEY_ENV, "").strip()
    if api_key:
        return api_key

    fallback_key = source_env.get(FALLBACK_API_KEY_ENV, "").strip()
    if fallback_key:
        return fallback_key

    raise ValueError(
        f"Missing API key. Set {PRIMARY_API_KEY_ENV}"
        f" or {FALLBACK_API_KEY_ENV} in the environment."
    )


def validate_input_file(path: str | Path) -> Path:
    input_path = Path(path).expanduser()
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported input file type: {input_path.suffix}. Supported: {supported}")
    return input_path.resolve()


def collect_input_files(path: str | Path) -> list[Path]:
    input_path = Path(path).expanduser()
    if not input_path.exists() or not input_path.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_path}")

    files = sorted(
        candidate.resolve()
        for candidate in input_path.rglob("*")
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        supported = ", ".join(sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"No supported input files found in directory: {input_path}. Supported: {supported}"
        )
    return files


def create_agent(*, model_name: str, api_key: str):
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    resolved_model_name = resolve_model_name(model_name)
    provider = GoogleProvider(api_key=api_key)
    model = GoogleModel(resolved_model_name, provider=provider)
    return Agent(model=model, output_type=ExtractionResult)


def _binary_content_from_path(path: Path):
    from pydantic_ai import BinaryContent

    return BinaryContent.from_path(path)


def extract_certificates(
    input_path: str | Path,
    model_name: str,
    *,
    api_key: str | None = None,
    env: Mapping[str, str] | None = None,
    agent_factory: Callable[..., object] | None = None,
    binary_content_factory: Callable[[Path], object] | None = None,
) -> ExtractionResult:
    validated_input = validate_input_file(input_path)
    resolved_api_key = api_key.strip() if isinstance(api_key, str) and api_key.strip() else load_api_key(env)
    agent_builder = create_agent if agent_factory is None else agent_factory
    binary_loader = _binary_content_from_path if binary_content_factory is None else binary_content_factory
    agent = agent_builder(model_name=model_name, api_key=resolved_api_key)
    prompt = f"{build_extraction_prompt()}\n\nNyni zpracuj prilozeny soubor."
    response = agent.run_sync([prompt, binary_loader(validated_input)])
    output = response.output
    if isinstance(output, ExtractionResult):
        return output
    if isinstance(output, Mapping):
        if "certificates" not in output:
            raise ValueError("Malformed extraction response: missing certificates")
        return ExtractionResult(
            certificates=[
                normalize_certificate_fields(certificate)
                for certificate in output.get("certificates", [])
            ]
        )
    raise TypeError("Unsupported extraction response type")


def build_extraction_prompt() -> str:
    topic_catalog = ", ".join(TOPIC_CATALOG)
    return f"""
### ROLE A CÍL ###
Jsi "Certifikátor v2.1", ultra-přesný AI asistent specializovaný na OCR extrakci dat z certifikátů a osvědčení o dalším vzdělávání pedagogických pracovníků (DVPP).

### KLÍČOVÝ KONTEXT A ZNALOSTI ###
* Jsi expert na terminologii v oblasti českého školství a DVPP.
* Rozumíš kontextu českých jmen a příjmení a jejich skloňování.
* Přiřazení kategorie "Téma" se řídí výhradně následujícím závazným číselníkem. Musíš dodržet přesné znění a malá písmena.

**ZÁVAZNÝ ČÍSELNÍK TÉMAT:**
* {topic_catalog}

### OMEZENÍ, PRAVIDLA A LOGIKA ZPRACOVÁNÍ ###
* Pokud si jakýmkoli údajem (jméno, datum, číslo) nejsi jistý na 100 % kvůli špatné kvalitě skenu, připoj za něj otazník.
* Pole "Téma" vyplňuj pouze a výhradně hodnotou ze závazného číselníku témat.
* Pole "Datum ukončení vzdělávání" je vždy termín konání vzdělávání. Pokud je vzdělávání více dnů, pak je to nejvyšší datum.
* Vždy dodrž strukturu polí:
Příjmení<TAB>Jméno<TAB>Datum narození<TAB>Název kurzu<TAB>Datum ukončení vzdělávání<TAB>Počet hodin<TAB><TAB>Téma
* Datum narození musí být vždy ve tvaru dd.mm.yyyy.
* Datum ukončení vzdělávání musí být vždy ve tvaru dd.mm.yyyy.
""".strip()


def serialize_result_json(result: ExtractionResult) -> str:
    payload = {"certificates": [asdict(record) for record in result.certificates]}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def serialize_result_tsv(result: ExtractionResult) -> str:
    return "\n".join(format_tsv_row(asdict(record)) for record in result.certificates)


def merge_extraction_results(results: list[ExtractionResult]) -> ExtractionResult:
    certificates: list[CertificateRecord] = []
    for result in results:
        certificates.extend(result.certificates)
    return ExtractionResult(certificates=certificates)


def format_tsv_row(record: Mapping[str, str]) -> str:
    fields = [
        record.get("surname", ""),
        record.get("name", ""),
        record.get("birth_date", ""),
        record.get("sablona", ""),
        record.get("course_name", ""),
        record.get("completion_date", ""),
        record.get("hours", ""),
        record.get("forma", ""),
        record.get("topic", ""),
    ]
    return "\t".join(str(field) for field in fields)
