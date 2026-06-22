#!/usr/bin/env python3

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
RENDERER_JS = REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"


def run_renderer_error_script(script_body: str):
    renderer_source = RENDERER_JS.read_text(encoding="utf-8")
    helper_start = renderer_source.index("function formatApiErrorMessage")
    helper_end = renderer_source.index("function getMessageContainer", helper_start)
    helper_source = renderer_source[helper_start:helper_end]
    node_script = textwrap.dedent(
        f"""
        {helper_source}
        {script_body}
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


class CertificateExportErrorUiTests(unittest.TestCase):
    def test_formatter_prefers_first_backend_error_detail(self) -> None:
        result = run_renderer_error_script(
            """
            const message = formatApiErrorMessage({
                message: 'ESF import selhal',
                errors: [
                    'Chybí číslo projektu.',
                    'Chybí datum vstupu.'
                ]
            });
            process.stdout.write(JSON.stringify({ message }));
            """
        )

        self.assertEqual(
            "ESF import selhal: Chybí číslo projektu. (+1 další detail)",
            result["message"],
        )

    def test_formatter_avoids_duplicate_when_message_already_contains_detail(self) -> None:
        result = run_renderer_error_script(
            """
            const message = formatApiErrorMessage({
                message: 'Chybí číslo projektu.',
                errors: ['Chybí číslo projektu.']
            });
            process.stdout.write(JSON.stringify({ message }));
            """
        )

        self.assertEqual("Chybí číslo projektu.", result["message"])


if __name__ == "__main__":
    unittest.main()
