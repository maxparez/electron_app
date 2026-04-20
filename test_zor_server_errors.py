import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

import server  # noqa: E402


class ZorServerErrorTests(unittest.TestCase):
    def test_zor_paths_endpoint_prefers_specific_warning_when_errors_are_empty(self) -> None:
        class FakeProcessor:
            def __init__(self, logger) -> None:
                self.logger = logger

            def process_paths(self, file_paths, output_dir, options):
                return {
                    "success": False,
                    "errors": [],
                    "warnings": ["Soubor ABC.xlsx má neplatný list Přehled"],
                    "info": [],
                }

        with patch.object(server, "ZorSpecDatProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/process/zor-spec-paths",
                json={
                    "filePaths": ["/tmp/ABC.xlsx"],
                    "options": {},
                    "autoSave": True,
                },
            )

        self.assertEqual(400, response.status_code)
        payload = response.get_json()
        self.assertEqual("error", payload["status"])
        self.assertEqual("Soubor ABC.xlsx má neplatný list Přehled", payload["message"])
        self.assertEqual(["Soubor ABC.xlsx má neplatný list Přehled"], payload["errors"])

    def test_zor_paths_endpoint_uses_explicit_fallback_when_processor_returns_no_detail(self) -> None:
        class FakeProcessor:
            def __init__(self, logger) -> None:
                self.logger = logger

            def process_paths(self, file_paths, output_dir, options):
                return {
                    "success": False,
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        with patch.object(server, "ZorSpecDatProcessor", FakeProcessor):
            response = server.app.test_client().post(
                "/api/process/zor-spec-paths",
                json={
                    "filePaths": ["/tmp/ABC.xlsx"],
                    "options": {},
                    "autoSave": True,
                },
            )

        self.assertEqual(400, response.status_code)
        payload = response.get_json()
        self.assertEqual("error", payload["status"])
        self.assertEqual(
            "Procesor nevrátil detailní chybu. Zkontrolujte logy server/tools.",
            payload["message"],
        )
        self.assertEqual(
            ["Procesor nevrátil detailní chybu. Zkontrolujte logy server/tools."],
            payload["errors"],
        )


if __name__ == "__main__":
    unittest.main()
