#!/usr/bin/env python3

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


class AttendanceSplitterUiStaticTests(unittest.TestCase):
    def test_index_contains_attendance_splitter_navigation_and_tool(self) -> None:
        html = (REPO_ROOT / "src" / "electron" / "renderer" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('data-tool="attendance-splitter"', html)
        self.assertIn("<span>Rozdělení docházky</span>", html)
        self.assertIn("<h3>✂️ Rozdělení docházky</h3>", html)
        self.assertIn('id="attendance-splitter-tool"', html)
        self.assertIn('id="select-attendance-splitter-files"', html)
        self.assertIn('id="select-attendance-splitter-folder"', html)
        self.assertIn('id="refresh-attendance-splitter-folder"', html)
        self.assertIn('id="attendance-splitter-files-list"', html)
        self.assertIn('id="process-attendance-splitter"', html)
        self.assertIn('id="attendance-splitter-results"', html)
        self.assertIn(
            "Z vybrané složky se načtou všechny docházky vhodné k rozdělení podle listů",
            html,
        )
        self.assertLess(
            html.index("<span>Rozdělení docházky</span>"),
            html.index("<span>Inovativní vzdělávání</span>"),
        )

    def test_renderer_wires_attendance_splitter_workflow(self) -> None:
        renderer = (
            REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"
        ).read_text(encoding="utf-8")

        self.assertIn("'attendance-splitter': []", renderer)
        self.assertIn("selectAttendanceSplitterFiles", renderer)
        self.assertIn("selectAttendanceSplitterFolder", renderer)
        self.assertIn("refreshAttendanceSplitterFolder", renderer)
        self.assertIn("updateAttendanceSplitterFilesList", renderer)
        self.assertIn("removeAttendanceSplitterFile", renderer)
        self.assertIn("checkAttendanceSplitterReady", renderer)
        self.assertIn("processAttendanceSplitter", renderer)
        self.assertIn("attendance-splitter/scan", renderer)
        self.assertIn("attendance-splitter/process", renderer)
        self.assertIn("rozdelene_dochazky", renderer)
        self.assertNotIn('onclick="removeAttendanceSplitterFile(', renderer)

    def test_legacy_windows_sync_includes_attendance_splitter_module(self) -> None:
        sync_script = (REPO_ROOT / "scripts" / "sync-to-windows-install.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "src/python/tools/attendance_splitter.py",
            sync_script,
        )


if __name__ == "__main__":
    unittest.main()
