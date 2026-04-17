#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))


class DvppCertificateUiStaticTests(unittest.TestCase):
    def test_i18n_loads_locale_from_parent_locales_directory(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "i18n.js").read_text(encoding="utf-8")

        self.assertIn("fetch(`../locales/${locale}.json`)", content)

    def test_index_html_contains_certificate_tool_navigation_and_panels(self) -> None:
        html = (REPO_ROOT / "src" / "electron" / "renderer" / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-tool="dvpp-certificates"', html)
        self.assertIn('id="dvpp-certificates-tool"', html)
        self.assertIn('id="cert-gemini-panel"', html)
        self.assertIn('id="cert-raw-panel"', html)
        self.assertIn('id="cert-files-list"', html)
        self.assertIn('id="cert-records-table"', html)
        self.assertIn('id="cert-diagnostics"', html)

    def test_renderer_js_wires_certificate_import_and_export_actions(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertIn("'dvpp-certificates': []", content)
        self.assertIn("loadCertificateMatches", content)
        self.assertIn("processCertificatesWithGemini", content)
        self.assertIn("processCertificatesFromRawText", content)
        self.assertIn("copyCertificateTsv", content)
        self.assertIn("saveCertificateExcel", content)
        self.assertIn("dvpp-certificates/scan", content)
        self.assertIn("dvpp-certificates/import/gemini", content)
        self.assertIn("dvpp-certificates/import/raw-text", content)
        self.assertIn("dvpp-certificates/export/tsv", content)
        self.assertIn("dvpp-certificates/export/excel", content)

    def test_renderer_js_avoids_inline_handlers_in_certificate_ui(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertNotIn('onchange="toggleCertificateFile(', content)
        self.assertNotIn('onchange="updateCertificateField(', content)
        self.assertNotIn('onclick="removeCertificateRecord(', content)

    def test_renderer_preserves_certificate_diagnostics_on_failed_import(self) -> None:
        renderer = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        preload = (REPO_ROOT / "src" / "electron" / "preload.js").read_text(encoding="utf-8")

        self.assertIn("error.data = result.data || null;", preload)
        self.assertIn("error.errors = result.errors || [];", preload)
        self.assertIn("if (error.data && error.data.batch)", renderer)
        self.assertIn("applyCertificateBatchResult(error.data.batch, error.data.diagnostics || []);", renderer)


if __name__ == "__main__":
    unittest.main()
