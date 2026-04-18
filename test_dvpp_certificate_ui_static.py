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
        self.assertIn('ag-grid.css', html)
        self.assertIn('ag-theme-alpine.css', html)
        self.assertIn('ag-grid-community.min.js', html)
        self.assertIn('id="cert-gemini-panel"', html)
        self.assertIn('id="cert-raw-panel"', html)
        self.assertIn('id="cert-files-list"', html)
        self.assertIn('id="cert-records-table"', html)
        self.assertIn('id="cert-bulk-template-select"', html)
        self.assertIn('id="cert-apply-template-all"', html)
        self.assertIn('id="cert-diagnostics"', html)
        self.assertIn('Hlavička evidence DVPP', html)
        self.assertIn('id="cert-fill-header"', html)

    def test_renderer_js_wires_certificate_import_and_export_actions(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertIn("'dvpp-certificates': []", content)
        self.assertIn("TEMPLATE_OPTIONS", content)
        self.assertIn("createCertificateGrid", content)
        self.assertIn("ensureCertificateGridApi", content)
        self.assertIn("setGridOption('rowData'", content)
        self.assertIn("loadCertificateMatches", content)
        self.assertIn("processCertificatesWithGemini", content)
        self.assertIn("processCertificatesFromRawText", content)
        self.assertIn("copyCertificateTsv", content)
        self.assertIn("saveCertificateExcel", content)
        self.assertIn("applyCertificateTemplateToAllRecords", content)
        self.assertIn("autoLoadStoredGeminiApiKey", content)
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

    def test_renderer_supports_template_select_and_copy_feedback(self) -> None:
        renderer = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertIn("agSelectCellEditor", renderer)
        self.assertIn("cellEditorParams: { values: TEMPLATE_OPTIONS }", renderer)
        self.assertIn("singleClickEdit: true", renderer)
        self.assertNotIn("domLayout: 'autoHeight'", renderer)
        self.assertIn("TSV obsah byl zkopírován do schránky.", renderer)
        self.assertIn("setStatusMessage(successMessage, 4000);", renderer)
        self.assertIn("await openFile(result.data.output_path);", renderer)
        self.assertIn("certApplyTemplateAllBtn.addEventListener('click', applyCertificateTemplateToAllRecords);", renderer)

    def test_certificate_grid_styles_include_vertical_lines(self) -> None:
        styles = (REPO_ROOT / "src" / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("--ag-borders: solid 1px;", styles)
        self.assertIn("--ag-cell-horizontal-border: solid #dbe4f0;", styles)
        self.assertIn(".cert-records-table .ag-cell:not(:last-child)", styles)
        self.assertIn("border-right: 1px solid #dbe4f0;", styles)
        self.assertIn(".cert-review-main {\n    display: flex;\n    flex-direction: column;", styles)
        self.assertIn(".cert-review-main .form-group {\n    display: flex;\n    flex-direction: column;\n    flex: 1 1 auto;\n    min-height: 0;\n    margin-bottom: 0;", styles)
        self.assertIn("flex: 1 1 auto;", styles)
        self.assertIn("min-height: 320px;", styles)
        self.assertIn("height: 100%;", styles)
        self.assertIn("overflow: hidden;", styles)
        self.assertIn(".content {\n    flex: 1;\n    padding: 30px;\n    overflow-y: auto;\n    display: flex;\n    flex-direction: column;\n    min-height: 0;", styles)
        self.assertIn("#dvpp-certificates-tool.active", styles)
        self.assertIn("flex-direction: column;", styles)
        self.assertIn("flex: 1 1 auto;", styles)
        self.assertIn("min-height: 0;", styles)

    def test_renderer_does_not_block_excel_export_on_missing_header_fields(self) -> None:
        renderer = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertNotIn("validateCertificateExportMetadata()", renderer)
        self.assertNotIn("Vyplnění hlavičky evidence DVPP vyžaduje doplnit pole", renderer)
        self.assertIn("exportMetadata: state.certificateExtraction.exportMetadata", renderer)


if __name__ == "__main__":
    unittest.main()
