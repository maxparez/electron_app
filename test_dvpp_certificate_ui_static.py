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

        self.assertIn("font-src 'self' data:", html)
        self.assertIn('data-tool="dvpp-certificates"', html)
        self.assertIn('id="dvpp-certificates-tool"', html)
        self.assertIn('ag-grid.css', html)
        self.assertIn('ag-theme-alpine-no-font.css', html)
        self.assertNotIn('ag-theme-alpine.css', html)
        self.assertIn('ag-grid-community.min.js', html)
        self.assertIn('id="cert-gemini-panel"', html)
        self.assertIn('id="cert-raw-panel"', html)
        self.assertIn('id="open-cert-prompts-modal"', html)
        self.assertIn('id="cert-prompts-modal"', html)
        self.assertIn('id="close-cert-prompts-modal"', html)
        self.assertIn('id="clear-cert-raw-text"', html)
        self.assertIn('class="cert-section cert-import-block"', html)
        self.assertIn('class="cert-section cert-review-block"', html)
        self.assertIn('class="cert-section cert-export-block"', html)
        self.assertIn('class="cert-section cert-diagnostics-block"', html)
        self.assertIn('class="cert-export-grid"', html)
        self.assertIn('class="cert-export-card cert-excel-export-card"', html)
        self.assertIn('class="cert-export-card cert-esf-export-card"', html)
        self.assertIn('class="cert-bulk-label" for="cert-bulk-template-select"', html)
        self.assertIn('class="cert-bulk-label" for="cert-bulk-forma-select"', html)
        self.assertIn('class="cert-bulk-label" for="cert-bulk-pohlavi-select"', html)
        self.assertIn('class="btn btn-secondary cert-action-btn" id="cert-apply-template-all"', html)
        self.assertIn('class="btn btn-secondary cert-action-btn" id="cert-apply-forma-all"', html)
        self.assertIn('class="btn btn-secondary cert-action-btn" id="cert-apply-pohlavi-all"', html)
        self.assertIn('id="cert-files-list"', html)
        self.assertIn('id="cert-records-table"', html)
        self.assertIn('id="cert-bulk-template-select"', html)
        self.assertIn('id="cert-apply-template-all"', html)
        self.assertIn('id="cert-bulk-forma-select"', html)
        self.assertIn('id="cert-apply-forma-all"', html)
        self.assertIn('id="cert-bulk-pohlavi-select"', html)
        self.assertIn('id="cert-apply-pohlavi-all"', html)
        self.assertIn('class="btn btn-success cert-mode-btn active" id="cert-mode-gemini"', html)
        self.assertIn('class="btn btn-secondary cert-import-toggle-btn" id="cert-toggle-import-panel" type="button" disabled', html)
        self.assertIn('>Zobrazit import</button>', html)
        self.assertIn('akreditovaný kurz průběžné DVPP', html)
        self.assertIn('kvalifikační_studium_DVPP', html)
        self.assertIn('supevize', html)
        self.assertNotIn('akreditovaný kurz při DVPP', html)
        self.assertNotIn('kvalifikační studium_DVPP', html)
        self.assertNotIn('supervize', html)
        self.assertIn('id="cert-toggle-import-panel"', html)
        self.assertIn('id="save-cert-esf"', html)
        self.assertIn('id="cert-diagnostics"', html)
        self.assertIn('Hlavička evidence DVPP', html)
        self.assertIn('Potřebujete prompt do GAI?', html)
        self.assertIn('Prompty pro Google AI Studio', html)
        self.assertIn('id="cert-fill-header"', html)
        self.assertIn('id="cert-esf-entry-date"', html)
        self.assertIn('id="cert-esf-exit-date"', html)
        self.assertLess(html.index('class="cert-section cert-import-block"'), html.index('class="cert-section cert-review-block"'))
        self.assertLess(html.index('class="cert-section cert-review-block"'), html.index('class="cert-section cert-export-block"'))
        self.assertLess(html.index('class="cert-section cert-export-block"'), html.index('class="cert-section cert-diagnostics-block"'))
        self.assertLess(html.index('for="cert-template-path"'), html.index('id="cert-project-number"'))
        self.assertLess(html.index('<span>Vytěžování certifikátů</span>'), html.index('<span>DVPP report</span>'))
        self.assertLess(html.index('<h3>🧾 Vytěžování certifikátů</h3>'), html.index('<h3>📚 DVPP report</h3>'))
        self.assertLess(html.index('<span>Vytěžování certifikátů</span>'), html.index('<span>Generátor plakátů</span>'))
        self.assertLess(html.index('<h3>🧾 Vytěžování certifikátů</h3>'), html.index('<h3>🖼️ Generátor plakátů</h3>'))
        self.assertLess(html.index('id="save-cert-excel"'), html.index('id="save-cert-tsv"'))
        self.assertLess(html.index('id="save-cert-tsv"'), html.index('id="copy-cert-tsv"'))
        self.assertIn('class="btn btn-primary cert-action-btn" id="save-cert-esf"', html)

    def test_renderer_js_wires_certificate_import_and_export_actions(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")
        switch_mode_body = content.split("function switchCertificateMode(mode) {", 1)[1].split("function syncCertificateImportPanels()", 1)[0]

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
        self.assertIn("saveCertificateEsfImport", content)
        self.assertIn("openCertificatePromptsModal", content)
        self.assertIn("closeCertificatePromptsModal", content)
        self.assertIn("clearCertificateRawText", content)
        self.assertIn("resetCertificateExtractionOutput", content)
        self.assertIn("applyCertificateTemplateToAllRecords", content)
        self.assertIn("applyCertificateFormaToAllRecords", content)
        self.assertIn("applyCertificatePohlaviToAllRecords", content)
        self.assertIn("setCertificateImportCollapsed", content)
        self.assertIn("if (state.certificateExtraction.importCollapsed) {", switch_mode_body)
        self.assertIn("setCertificateImportCollapsed(false);", switch_mode_body)
        self.assertIn("autoLoadStoredGeminiApiKey", content)
        self.assertIn("dvpp-certificates/scan", content)
        self.assertIn("dvpp-certificates/import/gemini", content)
        self.assertIn("dvpp-certificates/import/raw-text", content)
        self.assertIn("dvpp-certificates/export/tsv", content)
        self.assertIn("dvpp-certificates/export/excel", content)
        self.assertIn("dvpp-certificates/export/esf", content)
        self.assertIn(
            "mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence",
            content,
        )
        self.assertIn(
            "management škol, řízení organizace, leadership a řízení pedagogického procesu",
            content,
        )
        self.assertIn("profesní rozvoj ostatních pracovníků ve vzdělávání", content)
        self.assertIn("akreditovaný kurz průběžné DVPP", content)
        self.assertIn("kvalifikační_studium_DVPP", content)
        self.assertIn("supevize", content)
        self.assertIn("POHZENY", content)
        self.assertIn("POHMUZI", content)
        self.assertNotIn("akreditovaný kurz při DVPP", content)
        self.assertNotIn("kvalifikační studium_DVPP", content)
        self.assertNotIn("supervize", content)

    def test_renderer_js_avoids_inline_handlers_in_certificate_ui(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertNotIn('onchange="toggleCertificateFile(', content)
        self.assertNotIn('onchange="updateCertificateField(', content)
        self.assertNotIn('onclick="removeCertificateRecord(', content)

    def test_renderer_js_avoids_inline_handlers_in_shared_results_ui(self) -> None:
        content = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertNotIn('onclick="openFile(', content)
        self.assertNotIn('onclick="openFolder(', content)
        self.assertNotIn('onclick="downloadFile(', content)
        self.assertNotIn('onclick="toggleCollapsible(', content)
        self.assertNotIn('onclick="removeFile(', content)
        self.assertNotIn('onclick="keepOnly16hFiles(', content)
        self.assertNotIn('onclick="keepOnly32hFiles(', content)
        self.assertNotIn('onclick="clearAllZorFiles(', content)
        self.assertNotIn('onchange="toggleDvppFile(', content)

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
        self.assertIn("cellEditorParams: { values: FORMA_OPTIONS }", renderer)
        self.assertIn("cellEditorParams: { values: POHLAVI_OPTIONS }", renderer)
        self.assertIn("theme: 'legacy'", renderer)
        self.assertIn("domLayout: 'autoHeight'", renderer)
        self.assertIn("singleClickEdit: true", renderer)
        self.assertNotIn("suppressRowClickSelection", renderer)
        self.assertIn("TSV obsah byl zkopírován do schránky.", renderer)
        self.assertIn("setStatusMessage(successMessage, 4000);", renderer)
        self.assertIn("await openFile(result.data.output_path);", renderer)
        self.assertIn("elements.certToggleImportPanelBtn.disabled = importVisible;", renderer)
        self.assertIn("elements.certToggleImportPanelBtn.textContent = 'Zobrazit import';", renderer)
        self.assertIn("elements.certModeGeminiBtn.classList.toggle('btn-success', mode === 'gemini');", renderer)
        self.assertIn("resetCertificateExtractionOutput();", renderer)
        self.assertIn("certApplyTemplateAllBtn.addEventListener('click', applyCertificateTemplateToAllRecords);", renderer)
        self.assertIn("certApplyFormaAllBtn.addEventListener('click', applyCertificateFormaToAllRecords);", renderer)
        self.assertIn("certApplyPohlaviAllBtn.addEventListener('click', applyCertificatePohlaviToAllRecords);", renderer)
        self.assertIn("certToggleImportPanelBtn.addEventListener('click', toggleCertificateImportPanel);", renderer)
        self.assertIn("certOpenPromptsModalBtn.addEventListener('click', openCertificatePromptsModal);", renderer)
        self.assertIn("certClosePromptsModalBtn.addEventListener('click', closeCertificatePromptsModal);", renderer)
        self.assertIn("certClearRawTextBtn.addEventListener('click', clearCertificateRawText);", renderer)
        self.assertIn("if (event.key === 'Escape' && !elements.certPromptsModal.hidden)", renderer)
        self.assertIn("setCertificateImportCollapsed(true);", renderer)
        self.assertNotIn("cert-review-side", renderer)

    def test_certificate_grid_styles_include_vertical_lines(self) -> None:
        styles = (REPO_ROOT / "src" / "electron" / "renderer" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("--ag-borders: solid 1px;", styles)
        self.assertIn("--ag-cell-horizontal-border: solid #dbe4f0;", styles)
        self.assertIn(".cert-records-table .ag-cell:not(:last-child)", styles)
        self.assertIn("border-right: 1px solid #dbe4f0;", styles)
        self.assertIn("min-height: 220px;", styles)
        self.assertIn("overflow: hidden;", styles)
        self.assertIn(".cert-bulk-label", styles)
        self.assertIn("grid-template-columns: auto minmax(260px, 340px) auto;", styles)
        self.assertIn(".cert-action-btn", styles)
        self.assertIn(".cert-prompt-entry", styles)
        self.assertIn(".cert-modal-overlay", styles)
        self.assertIn(".cert-modal", styles)
        self.assertIn(".cert-export-grid", styles)
        self.assertIn(".cert-export-card", styles)
        self.assertNotIn(".cert-review-layout {", styles)
        self.assertIn("@media (max-width: 980px)", styles)
        self.assertNotIn("@media (max-width: 1100px)", styles)
        self.assertNotIn(".cert-import-toggle-btn {\n    margin-left: auto;\n}", styles)

    def test_renderer_does_not_block_excel_export_on_missing_header_fields(self) -> None:
        renderer = (REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js").read_text(encoding="utf-8")

        self.assertNotIn("validateCertificateExportMetadata()", renderer)
        self.assertNotIn("Vyplnění hlavičky evidence DVPP vyžaduje doplnit pole", renderer)
        self.assertIn("exportMetadata: state.certificateExtraction.exportMetadata", renderer)


if __name__ == "__main__":
    unittest.main()
