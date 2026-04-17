#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_SRC = PROJECT_ROOT / "src" / "python"
if str(PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(PYTHON_SRC))

from dvpp_cert_extraction import SUPPORTED_MODELS, validate_input_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the DVPP certificate extraction POC on a single file."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to the input file.")
    parser.add_argument(
        "--model",
        required=True,
        choices=SUPPORTED_MODELS,
        help="Gemini model identifier to use for the extraction POC.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Optional path for the JSON output.",
    )
    parser.add_argument(
        "--output-tsv",
        type=Path,
        default=None,
        help="Optional path for the TSV output.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        validated_input = validate_input_file(args.input)
    except (FileNotFoundError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")

    print(
        f"Validated input {validated_input} for model {args.model}. "
        "Extraction is not implemented in this step."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
