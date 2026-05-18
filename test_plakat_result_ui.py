#!/usr/bin/env python3

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
RENDERER_JS = REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"


def build_result_html(result, save_results, target_folder):
    renderer_source = RENDERER_JS.read_text(encoding="utf-8")
    if "function buildPlakatResultHtml" not in renderer_source:
        return ""

    escape_start = renderer_source.index("function escapeHtml")
    escape_end = renderer_source.index("// Detect mixed versions", escape_start)
    helper_start = renderer_source.index("function buildPlakatResultHtml")
    helper_end = renderer_source.index("// Save plakat", helper_start)
    helper_source = renderer_source[escape_start:escape_end] + "\n" + renderer_source[helper_start:helper_end]

    node_script = textwrap.dedent(
        f"""
        {helper_source}
        const result = {json.dumps(result)};
        const saveResults = {json.dumps(save_results)};
        const targetFolder = {json.dumps(target_folder)};
        process.stdout.write(buildPlakatResultHtml(result, saveResults, targetFolder));
        """
    )
    completed = subprocess.run(
        ["node", "-e", node_script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return completed.stdout


class PlakatResultUiTests(unittest.TestCase):
    def test_partial_success_displays_failed_project_reasons(self) -> None:
        result = {
            "data": {
                "successful_projects": 4,
                "failed_projects": 2,
                "total_projects": 6,
                "output_files": [
                    {"filename": "14411_plakat.pdf", "size": 2048},
                    {"filename": "14711_plakat.pdf", "size": 2048},
                    {"filename": "15391_plakat.pdf", "size": 2048},
                    {"filename": "13917_plakat.pdf", "size": 2048},
                ],
            },
            "errors": [
                "Project CZ.02.02.XX/00/24_034/0012741: Expected PDF but got text/html",
                "Project CZ.02.02.XX/00/24_034/0014201: Server error 500",
            ],
            "warnings": [],
        }
        save_results = [
            {"filename": "14411_plakat.pdf", "success": True},
            {"filename": "14711_plakat.pdf", "success": True},
            {"filename": "15391_plakat.pdf", "success": True},
            {"filename": "13917_plakat.pdf", "success": True},
        ]

        html = build_result_html(result, save_results, "C:\\Plakaty")

        self.assertIn("Nevygenerované plakáty", html)
        self.assertIn("CZ.02.02.XX/00/24_034/0012741", html)
        self.assertIn("CZ.02.02.XX/00/24_034/0014201", html)
        self.assertIn("Selhalo:</strong> 2", html)

    def test_partial_success_error_details_are_escaped(self) -> None:
        result = {
            "data": {"successful_projects": 1, "failed_projects": 1, "total_projects": 2, "output_files": []},
            "errors": ["Project <bad>: script & html"],
            "warnings": [],
        }

        html = build_result_html(result, [], "C:\\Plakaty")

        self.assertIn("Project &lt;bad&gt;: script &amp; html", html)
        self.assertNotIn("Project <bad>", html)


if __name__ == "__main__":
    unittest.main()
