#!/usr/bin/env python3

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
UPDATE_SCRIPT = REPO_ROOT / "scripts" / "update_windows.ps1"


class UpdateRestartScriptTests(unittest.TestCase):
    def test_update_script_restarts_application_after_successful_update(self) -> None:
        content = UPDATE_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('Join-Path $ResolvedRepoPath "start-app.bat"', content)
        self.assertIn("Start-Process", content)
        self.assertIn("-WorkingDirectory $resolvedRepoPath", content)
        self.assertIn("Aplikace se znovu spouští", content)


if __name__ == "__main__":
    unittest.main()
