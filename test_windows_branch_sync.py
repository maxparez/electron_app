#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from windows_branch_sync import classify_include_paths


class WindowsBranchSyncTests(unittest.TestCase):
    def test_classify_include_paths_splits_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "config").mkdir()
            (root / "README.md").write_text("hi", encoding="utf-8")

            files, directories = classify_include_paths(
                root,
                ["README.md", "src", "config", "docs/windows_install.html"],
            )

            self.assertEqual(["README.md", "docs/windows_install.html"], files)
            self.assertEqual(["config", "src"], directories)


if __name__ == "__main__":
    unittest.main()
