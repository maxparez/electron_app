#!/usr/bin/env python3

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check_electron_runtime.js"


class ElectronRuntimeCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="electron-runtime-check-"))
        self.addCleanup(lambda: shutil.rmtree(self.temp_dir, ignore_errors=True))

        self.electron_dir = self.temp_dir / "node_modules" / "electron"
        self.dist_dir = self.electron_dir / "dist"
        self.dist_dir.mkdir(parents=True)

    def run_check(self):
        return subprocess.run(
            ["node", str(CHECK_SCRIPT), "--repair-path"],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
        )

    def test_repairs_path_txt_newline_when_electron_exe_exists(self) -> None:
        (self.dist_dir / "electron.exe").write_bytes(b"fake exe")
        (self.electron_dir / "path.txt").write_text("electron.exe\r\n", encoding="utf-8")

        completed = self.run_check()

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("electron.exe", (self.electron_dir / "path.txt").read_text(encoding="utf-8"))

    def test_fails_when_path_txt_points_to_missing_executable(self) -> None:
        (self.electron_dir / "path.txt").write_text("electron.exe", encoding="utf-8")

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("Missing Electron executable", completed.stderr)


if __name__ == "__main__":
    unittest.main()
