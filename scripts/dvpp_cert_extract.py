#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_SRC = PROJECT_ROOT / "src" / "python"
if str(PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(PYTHON_SRC))

from dvpp_cert_extraction import (
    SUPPORTED_MODELS,
    extract_certificates,
    serialize_result_json,
    serialize_result_tsv,
)


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
        result = extract_certificates(args.input, args.model)
    except (FileNotFoundError, ModuleNotFoundError, TypeError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")
    except Exception as exc:
        parser.exit(2, f"{exc}\n")

    json_output = serialize_result_json(result)
    tsv_output = serialize_result_tsv(result)

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(f"{json_output}\n", encoding="utf-8")

    if args.output_tsv is not None:
        args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
        args.output_tsv.write_text(f"{tsv_output}\n", encoding="utf-8")

    print(tsv_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
