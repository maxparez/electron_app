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

    def test_windows_installers_repair_broken_electron_runtime(self) -> None:
        helper = (REPO_ROOT / "scripts" / "check_electron_runtime.js").read_text(encoding="utf-8")
        self.assertIn("fs.existsSync(electronExecutable)", helper)
        self.assertIn("fs.writeFileSync(pathFile, executablePath", helper)
        self.assertIn(".trim()", helper)

        for script_name in ("install_windows.ps1", "update_windows.ps1"):
            content = (REPO_ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertIn("function Repair-ElectronRuntime", content)
            self.assertIn('node "scripts\\check_electron_runtime.js" "--repair-path"', content)
            self.assertIn("npm install --foreground-scripts", content)

        start_app = (REPO_ROOT / "start-app.bat").read_text(encoding="utf-8")
        self.assertIn("scripts\\check_electron_runtime.js", start_app)
        self.assertIn("npm install --foreground-scripts", start_app)

    def test_windows_npm_commands_always_install_electron_dev_dependencies(self) -> None:
        script_paths = [
            REPO_ROOT / "scripts" / "install_windows.ps1",
            REPO_ROOT / "scripts" / "update_windows.ps1",
            REPO_ROOT / "start-app.bat",
            REPO_ROOT / "install-windows-standalone.bat",
        ]

        for script_path in script_paths:
            content = script_path.read_text(encoding="utf-8")
            npm_install_commands = [
                line.strip()
                for line in content.splitlines()
                if line.strip().startswith(("npm ci", "npm install", "call npm ci", "call npm install"))
            ]
            self.assertTrue(npm_install_commands, f"No npm install command found in {script_path.name}")
            for command in npm_install_commands:
                self.assertIn(
                    "--include=dev",
                    command,
                    f"Electron can be omitted by production npm config: {script_path.name}: {command}",
                )

    def test_windows_branch_includes_electron_runtime_check(self) -> None:
        include_paths = {
            line.strip()
            for line in (REPO_ROOT / "config" / "windows_branch_include.txt")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        self.assertIn("scripts/check_electron_runtime.js", include_paths)

    def test_windows_entrypoint_scripts_use_crlf_line_endings(self) -> None:
        script_paths = [
            REPO_ROOT / "install-windows.bat",
            REPO_ROOT / "update-windows.bat",
            REPO_ROOT / "scripts" / "install_windows.ps1",
            REPO_ROOT / "scripts" / "update_windows.ps1",
        ]

        for script_path in script_paths:
            content = script_path.read_bytes()
            self.assertIn(b"\r\n", content, f"{script_path.name} should use CRLF line endings")
            self.assertNotIn(b"\n", content.replace(b"\r\n", b""), f"{script_path.name} contains LF-only line endings")

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

    def test_package_lock_is_compatible_with_strict_npm_ci(self) -> None:
        package_lock = json.loads((REPO_ROOT / "package-lock.json").read_text(encoding="utf-8"))

        self.assertIn("node_modules/encoding", package_lock["packages"])

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
