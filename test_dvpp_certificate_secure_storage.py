#!/usr/bin/env python3

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))


class DvppCertificateSecureStorageTests(unittest.TestCase):
    def test_package_json_declares_keytar_dependency(self) -> None:
        package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertIn("keytar", package_json["dependencies"])

    def test_preload_exposes_secure_gemini_api_key_bridge(self) -> None:
        preload_content = (REPO_ROOT / "src" / "electron" / "preload.js").read_text(encoding="utf-8")

        self.assertIn("getGeminiApiKeyStatus", preload_content)
        self.assertIn("getGeminiApiKey", preload_content)
        self.assertIn("saveGeminiApiKey", preload_content)
        self.assertIn("deleteGeminiApiKey", preload_content)
        self.assertIn("secure:gemini:getStatus", preload_content)
        self.assertIn("secure:gemini:get", preload_content)
        self.assertIn("secure:gemini:set", preload_content)
        self.assertIn("secure:gemini:delete", preload_content)

    def test_main_process_uses_keytar_for_gemini_api_key_storage(self) -> None:
        main_content = (REPO_ROOT / "src" / "electron" / "main.js").read_text(encoding="utf-8")

        self.assertIn("require('keytar')", main_content)
        self.assertIn("GEMINI_KEY_SERVICE", main_content)
        self.assertIn("GEMINI_KEY_ACCOUNT", main_content)
        self.assertIn("ipcMain.handle('secure:gemini:getStatus'", main_content)
        self.assertIn("ipcMain.handle('secure:gemini:get'", main_content)
        self.assertIn("ipcMain.handle('secure:gemini:set'", main_content)
        self.assertIn("ipcMain.handle('secure:gemini:delete'", main_content)
        self.assertIn("keytar.getPassword", main_content)
        self.assertIn("keytar.setPassword", main_content)
        self.assertIn("keytar.deletePassword", main_content)

    def test_main_process_does_not_store_gemini_api_key_in_plain_config(self) -> None:
        main_content = (REPO_ROOT / "src" / "electron" / "main.js").read_text(encoding="utf-8")

        self.assertNotIn("config.set('gemini", main_content)
        self.assertNotIn('config.set("gemini', main_content)


if __name__ == "__main__":
    unittest.main()
