#!/usr/bin/env python3

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
RENDERER_JS = REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"


def parse_projects_with_renderer(input_text: str):
    renderer_source = RENDERER_JS.read_text(encoding="utf-8")
    function_start = renderer_source.index("function parseProjectsInput")
    function_end = renderer_source.index("// Show/hide loading overlay", function_start)
    parser_source = renderer_source[function_start:function_end]

    node_script = textwrap.dedent(
        f"""
        {parser_source}
        const input = {json.dumps(input_text)};
        process.stdout.write(JSON.stringify(parseProjectsInput(input)));
        """
    )
    completed = subprocess.run(
        ["node", "-e", node_script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return json.loads(completed.stdout)


def parse_projects_detailed_with_renderer(input_text: str):
    renderer_source = RENDERER_JS.read_text(encoding="utf-8")
    function_start = renderer_source.index("function parseProjectsInput")
    function_end = renderer_source.index("// Show/hide loading overlay", function_start)
    parser_source = renderer_source[function_start:function_end]

    node_script = textwrap.dedent(
        f"""
        {parser_source}
        const input = {json.dumps(input_text)};
        process.stdout.write(JSON.stringify(parseProjectsInputDetailed(input)));
        """
    )
    completed = subprocess.run(
        ["node", "-e", node_script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return json.loads(completed.stdout)


class PlakatProjectParsingTests(unittest.TestCase):
    def test_parses_bare_registration_number_as_project(self) -> None:
        project_id = "CZ.02.02.03/00/24_034/0010781"

        projects = parse_projects_with_renderer(project_id)

        self.assertEqual([{"id": project_id, "name": project_id}], projects)

    def test_parses_bare_registration_number_with_xx_program_code(self) -> None:
        project_id = "CZ.02.02.XX/00/24_034/0012741"

        projects = parse_projects_with_renderer(project_id)

        self.assertEqual([{"id": project_id, "name": project_id}], projects)

    def test_parses_registration_number_followed_by_name(self) -> None:
        project_id = "CZ.02.02.03/00/24_034/0010781"

        projects = parse_projects_with_renderer(f"{project_id} Testovací projekt")

        self.assertEqual([{"id": project_id, "name": "Testovací projekt"}], projects)

    def test_keeps_semicolon_project_format(self) -> None:
        project_id = "CZ.02.02.03/00/24_034/0010781"

        projects = parse_projects_with_renderer(f"{project_id};Testovací projekt")

        self.assertEqual([{"id": project_id, "name": "Testovací projekt"}], projects)

    def test_detailed_parser_reports_invalid_bare_project_lines(self) -> None:
        valid_project_id = "CZ.02.02.03/00/24_034/0010781"
        input_text = "\n".join(
            [
                "spatne-cislo-1",
                valid_project_id,
                "CZ.02.02/00/24_034/0010782",
            ]
        )

        result = parse_projects_detailed_with_renderer(input_text)

        self.assertEqual([{"id": valid_project_id, "name": valid_project_id}], result["projects"])
        self.assertEqual(["spatne-cislo-1", "CZ.02.02/00/24_034/0010782"], result["invalidLines"])


if __name__ == "__main__":
    unittest.main()
