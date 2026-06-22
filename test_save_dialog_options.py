#!/usr/bin/env python3

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def run_node(script: str):
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return json.loads(completed.stdout)


class SaveDialogOptionsTests(unittest.TestCase):
    def test_xlsx_default_name_prefers_excel_filter(self) -> None:
        result = run_node(
            textwrap.dedent(
                """
                const assert = require('assert');
                const { buildSaveDialogOptions } = require('./src/electron/save-dialog-options');

                const options = buildSaveDialogOptions('dvpp_certificates.xlsx');

                assert.strictEqual(options.defaultPath, 'dvpp_certificates.xlsx');
                assert.strictEqual(options.filters[0].name, 'Excel Files');
                assert.deepStrictEqual(options.filters[0].extensions, ['xlsx']);
                process.stdout.write(JSON.stringify(options));
                """
            )
        )

        self.assertEqual("Excel Files", result["filters"][0]["name"])

    def test_pdf_default_name_prefers_pdf_filter(self) -> None:
        result = run_node(
            textwrap.dedent(
                """
                const assert = require('assert');
                const { buildSaveDialogOptions } = require('./src/electron/save-dialog-options');

                const options = buildSaveDialogOptions('plakat.pdf');

                assert.strictEqual(options.filters[0].name, 'PDF Files');
                assert.deepStrictEqual(options.filters[0].extensions, ['pdf']);
                process.stdout.write(JSON.stringify(options));
                """
            )
        )

        self.assertEqual("PDF Files", result["filters"][0]["name"])


if __name__ == "__main__":
    unittest.main()
