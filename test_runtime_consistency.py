#!/usr/bin/env python3

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

import server


REPO_ROOT = Path(__file__).resolve().parent


class RuntimeConsistencyTests(unittest.TestCase):
    def test_preload_does_not_import_main_process_config_module(self) -> None:
        preload_path = REPO_ROOT / "src" / "electron" / "preload.js"
        content = preload_path.read_text(encoding="utf-8")

        self.assertNotIn("require('./config')", content)
        self.assertIn("config:get", content)

    def test_renderer_html_declares_content_security_policy(self) -> None:
        index_path = REPO_ROOT / "src" / "electron" / "renderer" / "index.html"
        content = index_path.read_text(encoding="utf-8")

        self.assertIn('http-equiv="Content-Security-Policy"', content)

    def test_electron_runtime_does_not_hardcode_backend_port(self) -> None:
        runtime_files = [
            REPO_ROOT / "src" / "electron" / "main.js",
            REPO_ROOT / "src" / "electron" / "preload.js",
            REPO_ROOT / "src" / "electron" / "renderer" / "backend-monitor.js",
        ]

        offenders = []
        for file_path in runtime_files:
            content = file_path.read_text(encoding="utf-8")
            if "http://localhost:5000" in content:
                offenders.append(str(file_path.relative_to(REPO_ROOT)))

        self.assertEqual([], offenders, f"Hardcoded backend URL found in: {offenders}")

    def test_config_endpoint_reports_package_version(self) -> None:
        package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))

        response = server.app.test_client().get("/api/config")

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual(package_json["version"], payload["data"]["version"])
        tool_ids = [tool["id"] for tool in payload["data"]["tools"]]
        self.assertIn("dvpp-certificates", tool_ids)

    def test_install_windows_script_uses_existing_smoke_test_path(self) -> None:
        script_path = REPO_ROOT / "scripts" / "install_windows.ps1"
        content = script_path.read_text(encoding="utf-8")

        self.assertIn("test_students_16plus.py", content)
        self.assertNotIn("tests/test_students_16plus.py", content)

    def test_install_windows_batch_delegates_to_powershell_installer(self) -> None:
        batch_path = REPO_ROOT / "install-windows.bat"
        content = batch_path.read_text(encoding="utf-8")

        self.assertIn('scripts\\install_windows.ps1', content)
        self.assertIn('powershell -NoProfile -ExecutionPolicy Bypass -File "%INSTALL_SCRIPT%" %*', content)

    def test_main_window_defaults_to_wide_desktop_layout(self) -> None:
        main_js = (REPO_ROOT / "src" / "electron" / "main.js").read_text(encoding="utf-8")

        self.assertIn("width: 1600,", main_js)

    def test_environment_configs_match_release_version_family(self) -> None:
        package_version = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))["version"]
        production_config = json.loads((REPO_ROOT / "config" / "production.json").read_text(encoding="utf-8"))
        development_config = json.loads((REPO_ROOT / "config" / "development.json").read_text(encoding="utf-8"))
        electron_config = (REPO_ROOT / "src" / "electron" / "config.js").read_text(encoding="utf-8")

        self.assertEqual(package_version, production_config["app"]["version"])
        self.assertEqual(f"{package_version}-dev", development_config["app"]["version"])
        self.assertIn(f'version: "{package_version}"', electron_config)

    def test_plakat_endpoint_cleans_up_temporary_directory(self) -> None:
        temp_root = Path(tempfile.mkdtemp(prefix="plakat-endpoint-root-"))
        self.addCleanup(lambda: shutil.rmtree(temp_root, ignore_errors=True))

        temp_dir = temp_root / "plakat-output"
        temp_dir.mkdir()
        output_path = temp_dir / "poster.pdf"
        output_path.write_bytes(b"%PDF-1.4\n")

        class FakePlakatGenerator:
            def __init__(self, logger) -> None:
                self.logger = logger

            def process(self, files, options):
                return {
                    "success": True,
                    "message": "ok",
                    "data": {
                        "successful_projects": 1,
                        "failed_projects": 0,
                        "total_projects": 1,
                        "output_files": [str(output_path)],
                    },
                    "errors": [],
                    "warnings": [],
                    "info": [],
                }

        request_payload = {
            "projects": [{"id": "CZ.00/00", "name": "Test project"}],
            "orientation": "portrait",
            "common_text": "Test",
        }

        with patch.object(server.tempfile, "mkdtemp", return_value=str(temp_dir)):
            with patch.object(server, "PlakatGenerator", FakePlakatGenerator):
                response = server.app.test_client().post("/api/process/plakat", json=request_payload)

        self.assertEqual(200, response.status_code)
        self.assertFalse(temp_dir.exists(), f"Temporary directory was not removed: {temp_dir}")


if __name__ == "__main__":
    unittest.main()
