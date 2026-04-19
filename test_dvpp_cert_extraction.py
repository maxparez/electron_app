#!/usr/bin/env python3

import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from dvpp_cert_extraction import (
    CertificateRecord,
    ExtractionResult,
    build_extraction_prompt,
    collect_input_files,
    extract_certificates,
    format_tsv_row,
    load_api_key,
    normalize_date,
    normalize_topic,
    resolve_model_name,
    serialize_result_json,
    serialize_result_tsv,
    strip_titles,
    validate_input_file,
)


class DvppCertExtractionTests(unittest.TestCase):
    def _load_cli_module(self):
        module_path = Path(__file__).resolve().parent / "scripts" / "dvpp_cert_extract.py"
        spec = importlib.util.spec_from_file_location("dvpp_cert_extract_cli", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load CLI module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_format_tsv_row_uses_expected_field_order(self) -> None:
        record = {
            "surname": "Novakova",
            "name": "Jana",
            "birth_date": "05.09.1980",
            "sablona": "vzdělávání ZŠ_2_II_4",
            "course_name": "Kurz AI ve vyuce",
            "completion_date": "14.03.2024",
            "hours": "8",
            "forma": "neakreditovaný kurz",
            "topic": "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
        }

        self.assertEqual(
            "Novakova\tJana\t05.09.1980\tvzdělávání ZŠ_2_II_4\tKurz AI ve vyuce\t14.03.2024\t8\tneakreditovaný kurz\tmediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            format_tsv_row(record),
        )

    def test_normalize_topic_enforces_whitelist(self) -> None:
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            normalize_topic("umela inteligence"),
        )
        self.assertEqual("", normalize_topic("finance a ucetnictvi"))

    def test_normalize_date_returns_dd_mm_yyyy(self) -> None:
        self.assertEqual("07.03.2024", normalize_date("2024-03-07"))
        self.assertEqual("07.03.2024", normalize_date("7.3.2024"))
        self.assertEqual("07.03.2024", normalize_date("07/03/2024"))

    def test_validate_input_file_accepts_supported_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            for extension in ("pdf", "jpg", "jpeg", "png"):
                input_path = base_dir / f"certificate.{extension}"
                input_path.write_text("sample", encoding="utf-8")

                self.assertEqual(input_path.resolve(), validate_input_file(input_path))

    def test_validate_input_file_rejects_unsupported_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "certificate.txt"
            input_path.write_text("sample", encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_input_file(input_path)

    def test_collect_input_files_returns_supported_files_from_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "b.pdf").write_text("sample", encoding="utf-8")
            (root / "a.png").write_text("sample", encoding="utf-8")
            (root / "ignore.txt").write_text("sample", encoding="utf-8")
            nested = root / "nested"
            nested.mkdir()
            (nested / "c.jpg").write_text("sample", encoding="utf-8")

            self.assertEqual(
                [
                    (root / "a.png").resolve(),
                    (root / "b.pdf").resolve(),
                    (nested / "c.jpg").resolve(),
                ],
                collect_input_files(root),
            )

    def test_collect_input_files_rejects_directory_without_supported_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "ignore.txt").write_text("sample", encoding="utf-8")

            with self.assertRaises(ValueError):
                collect_input_files(root)

    def test_strip_titles_removes_academic_prefixes_and_suffixes(self) -> None:
        self.assertEqual("Jana", strip_titles("Mgr. Jana, Ph.D."))
        self.assertEqual("Novakova", strip_titles("Bc. Novakova, DiS."))

    def test_certificate_record_validates_required_fields(self) -> None:
        record = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)
        self.assertEqual("05.09.1980", record.birth_date)
        self.assertEqual("Kurz AI ve vyuce", record.course_name)
        self.assertEqual("14.03.2024", record.completion_date)
        self.assertEqual("8", record.hours)
        self.assertEqual(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            record.topic,
        )

        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="",
                name="Jana",
                birth_date="05.09.1980",
                course_name="Kurz AI ve vyuce",
                completion_date="14.03.2024",
                hours="8",
                topic="umela inteligence",
            )

    def test_certificate_record_rejects_invalid_dates(self) -> None:
        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="Novakova",
                name="Jana",
                birth_date="1980/99/99",
                course_name="Kurz AI ve vyuce",
                completion_date="14.03.2024",
                hours="8",
                topic="umela inteligence",
            )

        with self.assertRaises(ValueError):
            CertificateRecord(
                surname="Novakova",
                name="Jana",
                birth_date="05.09.1980",
                course_name="Kurz AI ve vyuce",
                completion_date="31.02.2024",
                hours="8",
                topic="umela inteligence",
            )

    def test_certificate_record_allows_uncertain_dates_with_question_mark(self) -> None:
        record = CertificateRecord(
            surname="Novakova",
            name="Jana",
            birth_date="05.09.1980?",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024?",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("05.09.1980?", record.birth_date)
        self.assertEqual("14.03.2024?", record.completion_date)

    def test_certificate_record_strips_titles_from_name_and_surname(self) -> None:
        record = CertificateRecord(
            surname="Bc. Novakova, DiS.",
            name="Mgr. Jana, Ph.D.",
            birth_date="05.09.1980",
            course_name="Kurz AI ve vyuce",
            completion_date="14.03.2024",
            hours="8",
            topic="umela inteligence",
        )

        self.assertEqual("Novakova", record.surname)
        self.assertEqual("Jana", record.name)

    def test_extraction_result_requires_certificate_list(self) -> None:
        result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Novakova",
                    name="Jana",
                    birth_date="05.09.1980",
                    course_name="Kurz AI ve vyuce",
                    completion_date="14.03.2024",
                    hours="8",
                    topic="umela inteligence",
                )
            ]
        )

        self.assertEqual(1, len(result.certificates))
        self.assertEqual("Novakova", result.certificates[0].surname)

        with self.assertRaises(TypeError):
            ExtractionResult(certificates="not-a-list")

    def test_extraction_result_rejects_non_certificate_item(self) -> None:
        with self.assertRaises(TypeError):
            ExtractionResult(certificates=["not-a-record"])

    def test_build_extraction_prompt_includes_required_instructions_and_topic_catalog(self) -> None:
        prompt = build_extraction_prompt()

        self.assertIn('Jsi "Certifikátor v2.1"', prompt)
        self.assertIn("Datum narození", prompt)
        self.assertIn("Pokud si jakýmkoli údajem", prompt)
        self.assertIn(
            "Příjmení<TAB>Jméno<TAB>Datum narození<TAB>Název kurzu<TAB>Datum ukončení vzdělávání<TAB>Počet hodin<TAB><TAB>Téma",
            prompt,
        )
        self.assertIn("umělá inteligence", prompt)
        self.assertIn("pedagogická diagnostika", prompt)
        self.assertIn("well-being a psychohygiena", prompt)
        self.assertIn("podpora uvádějících/provázejících učitelů", prompt)
        self.assertIn(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            prompt,
        )
        self.assertIn(
            "management škol, řízení organizace, leadership a řízení pedagogického procesu",
            prompt,
        )
        self.assertIn("profesní rozvoj ostatních pracovníků ve vzdělávání", prompt)

    def test_resolve_model_name_accepts_supported_gemini_models(self) -> None:
        self.assertEqual(
            "gemini-3-flash-preview",
            resolve_model_name("gemini-3-flash-preview"),
        )
        self.assertEqual(
            "gemini-3.1-pro-preview",
            resolve_model_name("gemini-3.1-pro-preview"),
        )

    def test_load_api_key_prefers_gemini_api_key(self) -> None:
        self.assertEqual(
            "gemini-secret",
            load_api_key(
                {
                    "GEMINI_API_KEY": " gemini-secret ",
                    "GOOGLE_API_KEY": "google-secret",
                }
            ),
        )

    def test_extract_certificates_uses_agent_factory_binary_content_and_serializers(self) -> None:
        expected_result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Novakova",
                    name="Jana",
                    birth_date="1980-09-05",
                    course_name="Kurz AI ve vyuce",
                    completion_date="2024-03-14",
                    hours="8",
                    topic="umela inteligence",
                )
            ]
        )

        class FakeAgent:
            def __init__(self) -> None:
                self.calls = []

            def run_sync(self, payload):
                self.calls.append(payload)
                return SimpleNamespace(output=expected_result)

        created_agents = []

        def fake_agent_factory(*, model_name: str, api_key: str):
            self.assertEqual("gemini-3-flash-preview", model_name)
            self.assertEqual("gemini-secret", api_key)
            agent = FakeAgent()
            created_agents.append(agent)
            return agent

        seen_paths = []

        def fake_binary_content_factory(path: Path):
            seen_paths.append(path)
            return "BINARY_CONTENT"

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "certificate.pdf"
            input_path.write_bytes(b"%PDF-1.4")

            result = extract_certificates(
                input_path,
                "gemini-3-flash-preview",
                env={"GEMINI_API_KEY": "gemini-secret"},
                agent_factory=fake_agent_factory,
                binary_content_factory=fake_binary_content_factory,
            )

        self.assertEqual(expected_result, result)
        self.assertEqual([input_path.resolve()], seen_paths)
        self.assertEqual(1, len(created_agents))
        self.assertEqual(1, len(created_agents[0].calls))
        self.assertEqual("BINARY_CONTENT", created_agents[0].calls[0][1])
        self.assertIn("Nyni zpracuj prilozeny soubor.", created_agents[0].calls[0][0])
        self.assertIn('"surname": "Novakova"', serialize_result_json(result))
        self.assertEqual(
            "Novakova\tJana\t05.09.1980\t\tKurz AI ve vyuce\t14.03.2024\t8\t\tmediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            serialize_result_tsv(result),
        )

    def test_extract_certificates_rejects_mapping_without_certificates_key(self) -> None:
        class FakeAgent:
            def run_sync(self, payload):
                return SimpleNamespace(output={"items": []})

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "certificate.pdf"
            input_path.write_bytes(b"%PDF-1.4")

            with self.assertRaises(ValueError):
                extract_certificates(
                    input_path,
                    "gemini-3-flash-preview",
                    env={"GEMINI_API_KEY": "gemini-secret"},
                    agent_factory=lambda **_kwargs: FakeAgent(),
                    binary_content_factory=lambda _path: "BINARY_CONTENT",
                )

    def test_cli_parse_args_supports_required_and_optional_arguments(self) -> None:
        cli_module = self._load_cli_module()

        parsed = cli_module.parse_args(
            [
                "--input",
                "sample.pdf",
                "--model",
                "gemini-3-flash-preview",
                "--output-json",
                "result.json",
                "--output-tsv",
                "result.tsv",
            ]
        )

        self.assertEqual(Path("sample.pdf"), parsed.input)
        self.assertEqual("gemini-3-flash-preview", parsed.model)
        self.assertEqual(Path("result.json"), parsed.output_json)
        self.assertEqual(Path("result.tsv"), parsed.output_tsv)

    def test_cli_parse_args_defaults_optional_output_paths_to_none(self) -> None:
        cli_module = self._load_cli_module()

        parsed = cli_module.parse_args(
            [
                "--input",
                "sample.png",
                "--model",
                "gemini-3.1-pro-preview",
            ]
        )

        self.assertEqual(Path("sample.png"), parsed.input)
        self.assertEqual("gemini-3.1-pro-preview", parsed.model)
        self.assertIsNone(parsed.output_json)
        self.assertIsNone(parsed.output_tsv)

    def test_cli_parse_args_supports_input_directory(self) -> None:
        cli_module = self._load_cli_module()

        parsed = cli_module.parse_args(
            [
                "--input-dir",
                "batch",
                "--model",
                "gemini-3-flash-preview",
            ]
        )

        self.assertEqual(Path("batch"), parsed.input_dir)
        self.assertIsNone(parsed.input)

    def test_cli_main_prints_tsv_and_writes_optional_outputs(self) -> None:
        cli_module = self._load_cli_module()
        extraction_result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Novakova",
                    name="Jana",
                    birth_date="05.09.1980",
                    course_name="Kurz AI ve vyuce",
                    completion_date="14.03.2024",
                    hours="8",
                    topic="umela inteligence",
                )
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            json_path = temp_path / "result.json"
            tsv_path = temp_path / "result.tsv"
            input_path = temp_path / "certificate.pdf"
            input_path.write_bytes(b"%PDF-1.4")

            with (
                patch.object(
                    cli_module,
                    "extract_certificates",
                    return_value=extraction_result,
                ) as mocked_extract,
                patch.object(sys, "stdout", new_callable=io.StringIO) as stdout,
            ):
                exit_code = cli_module.main(
                    [
                        "--input",
                        str(input_path),
                        "--model",
                        "gemini-3-flash-preview",
                        "--output-json",
                        str(json_path),
                        "--output-tsv",
                        str(tsv_path),
                    ]
                )

            json_output = json_path.read_text(encoding="utf-8")
            tsv_output = tsv_path.read_text(encoding="utf-8")
            stdout_output = stdout.getvalue()

        self.assertEqual(0, exit_code)
        mocked_extract.assert_called_once_with(input_path, "gemini-3-flash-preview")
        self.assertIn("Novakova\tJana\t05.09.1980", stdout_output)
        self.assertIn('"surname": "Novakova"', json_output)
        self.assertIn(
            "Novakova\tJana\t05.09.1980\t\tKurz AI ve vyuce\t14.03.2024\t8\t\tmediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            tsv_output,
        )

    def test_cli_main_batches_directory_as_one_file_per_request(self) -> None:
        cli_module = self._load_cli_module()

        first_result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Novakova",
                    name="Jana",
                    birth_date="05.09.1980",
                    course_name="Kurz AI",
                    completion_date="14.03.2024",
                    hours="8",
                    topic="umela inteligence",
                )
            ]
        )
        second_result = ExtractionResult(
            certificates=[
                CertificateRecord(
                    surname="Svobodova",
                    name="Marie",
                    birth_date="24.07.2000",
                    course_name="Kurz Wellbeing",
                    completion_date="24.03.2025",
                    hours="8",
                    topic="well-being a psychohygiena",
                )
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            batch_dir = Path(temp_dir) / "batch"
            batch_dir.mkdir()
            first_file = batch_dir / "a.pdf"
            second_file = batch_dir / "b.png"
            first_file.write_bytes(b"%PDF-1.4")
            second_file.write_bytes(b"png")

            with (
                patch.object(
                    cli_module,
                    "extract_certificates",
                    side_effect=[first_result, second_result],
                ) as mocked_extract,
                patch.object(sys, "stdout", new_callable=io.StringIO) as stdout,
            ):
                exit_code = cli_module.main(
                    [
                        "--input-dir",
                        str(batch_dir),
                        "--model",
                        "gemini-3-flash-preview",
                    ]
                )

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [
                (first_file.resolve(), "gemini-3-flash-preview"),
                (second_file.resolve(), "gemini-3-flash-preview"),
            ],
            [call.args for call in mocked_extract.call_args_list],
        )
        self.assertIn("Novakova\tJana\t05.09.1980", stdout.getvalue())
        self.assertIn("Svobodova\tMarie\t24.07.2000", stdout.getvalue())

    def test_cli_main_exits_cleanly_on_unexpected_extraction_error(self) -> None:
        cli_module = self._load_cli_module()

        class ProviderFailure(Exception):
            pass

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "certificate.pdf"
            input_path.write_bytes(b"%PDF-1.4")

            with (
                patch.object(
                    cli_module,
                    "extract_certificates",
                    side_effect=ProviderFailure("Gemini provider timeout"),
                ),
                patch.object(sys, "stderr", new_callable=io.StringIO) as stderr,
            ):
                with self.assertRaises(SystemExit) as exit_ctx:
                    cli_module.main(
                        [
                            "--input",
                            str(input_path),
                            "--model",
                            "gemini-3-flash-preview",
                        ]
                    )

            stderr_output = stderr.getvalue()

        self.assertEqual(2, exit_ctx.exception.code)
        self.assertIn("Gemini provider timeout", stderr_output)

    def test_requirements_pin_pydantic_ai_version(self) -> None:
        requirements_path = Path(__file__).resolve().parent / "requirements.txt"
        requirements_lines = requirements_path.read_text(encoding="utf-8").splitlines()

        self.assertIn("pydantic-ai-slim[google]==1.84.0", requirements_lines)

    def test_windows_requirements_pin_pydantic_ai_version(self) -> None:
        requirements_path = Path(__file__).resolve().parent / "requirements-windows.txt"
        requirements_lines = requirements_path.read_text(encoding="utf-8").splitlines()

        self.assertIn("pydantic-ai-slim[google]==1.84.0", requirements_lines)


if __name__ == "__main__":
    unittest.main()
