#!/usr/bin/env python3

import json
import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
RENDERER_JS = REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"


def run_update_ui_script(script_body: str):
    renderer_source = RENDERER_JS.read_text(encoding="utf-8")
    helper_start = renderer_source.index("function formatUpdatePromptMessage")
    helper_end = renderer_source.index("// Check backend connection", helper_start)
    helper_source = renderer_source[helper_start:helper_end]

    node_script = textwrap.dedent(
        f"""
        const window = {{}};
        const elements = {{
            updateCheckBtn: {{
                disabled: false,
                textContent: '',
                classList: {{ add() {{}}, remove() {{}} }}
            }},
            updateStatus: {{ textContent: '' }},
            updateModal: {{ hidden: true }},
            updateModalCurrentVersion: {{ textContent: '' }},
            updateModalLatestVersion: {{ textContent: '' }},
            updateModalChannel: {{ textContent: '' }},
            updateModalSummary: {{ textContent: '' }},
            updateModalChanges: {{ innerHTML: '' }}
        }};
        let pendingUpdateInfo = null;
        let automaticUpdatePromptShown = false;
        function setStatusMessage() {{}}
        function showMessage() {{}}
        function escapeHtml(value) {{
            return String(value)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }}
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


class UpdateAutoCheckUiTests(unittest.TestCase):
    def test_update_modal_renders_versions_and_escaped_release_notes(self) -> None:
        result = run_update_ui_script(
            """
            const html = renderUpdateReleaseNotes({
                branch: 'windows-install',
                currentVersion: '1.3.0',
                latestVersion: '1.4.0',
                releaseNotes: {
                    summary: 'Nové funkce a opravy.',
                    sections: {
                        features: [{
                            title: 'Rozdělení <docházky>',
                            description: 'Bezpečné & přehledné.'
                        }],
                        improvements: [],
                        fixes: []
                    }
                }
            });
            process.stdout.write(JSON.stringify({ html }));
            """
        )

        self.assertIn("Nové funkce", result["html"])
        self.assertIn("Rozdělení &lt;docházky&gt;", result["html"])
        self.assertIn("Bezpečné &amp; přehledné.", result["html"])

    def test_automatic_update_opens_modal_only_once(self) -> None:
        result = run_update_ui_script(
            """
            const calls = [];
            const updateInfo = {
                updateAvailable: true,
                branch: 'windows-install',
                latestSummary: 'abc123 [fix] Test'
            };

            (async () => {
                const first = await maybePromptForAutomaticUpdate(updateInfo, {
                    showModal: (info) => {
                        calls.push({ type: 'modal', info });
                    }
                });
                const second = await maybePromptForAutomaticUpdate(updateInfo, {
                    showModal: () => {
                        calls.push({ type: 'unexpected-modal' });
                    }
                });

                process.stdout.write(JSON.stringify({ first, second, calls }));
            })().catch((error) => {
                console.error(error);
                process.exit(1);
            });
            """
        )

        self.assertTrue(result["first"])
        self.assertFalse(result["second"])
        self.assertEqual(["modal"], [call["type"] for call in result["calls"]])

    def test_index_contains_custom_update_modal(self) -> None:
        html = (REPO_ROOT / "src" / "electron" / "renderer" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('id="update-modal"', html)
        self.assertIn('id="update-modal-changes"', html)
        self.assertIn('id="update-modal-install"', html)
        self.assertIn('id="update-modal-later"', html)
        self.assertIn("Co je nového", html)

    def test_renderer_no_longer_uses_native_confirm_for_updates(self) -> None:
        renderer = RENDERER_JS.read_text(encoding="utf-8")

        self.assertNotIn("window.confirm(formatUpdatePromptMessage", renderer)
        self.assertIn("openUpdateModal", renderer)
        self.assertIn("closeUpdateModal", renderer)


if __name__ == "__main__":
    unittest.main()
