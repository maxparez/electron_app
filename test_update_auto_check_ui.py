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
            updateStatus: {{ textContent: '' }}
        }};
        let pendingUpdateInfo = null;
        let automaticUpdatePromptShown = false;
        function setStatusMessage() {{}}
        function showMessage() {{}}
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
    def test_prompt_message_mentions_update_and_restart(self) -> None:
        result = run_update_ui_script(
            """
            const message = formatUpdatePromptMessage({
                branch: 'windows-install',
                latestSummary: 'cdcbe6c [release] Pseudo update for updater test'
            }, { automatic: true });
            process.stdout.write(JSON.stringify({ message }));
            """
        )

        self.assertIn("Je dostupná nová verze aplikace", result["message"])
        self.assertIn("cdcbe6c", result["message"])
        self.assertIn("restartovat aplikaci", result["message"])

    def test_automatic_prompt_starts_update_once_without_second_confirmation(self) -> None:
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
                    prompt: (message) => {
                        calls.push({ type: 'prompt', message });
                        return true;
                    },
                    startUpdate: async (options) => {
                        calls.push({ type: 'start', options });
                    }
                });
                const second = await maybePromptForAutomaticUpdate(updateInfo, {
                    prompt: () => {
                        calls.push({ type: 'unexpected-prompt' });
                        return true;
                    },
                    startUpdate: async () => {
                        calls.push({ type: 'unexpected-start' });
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
        self.assertEqual(["prompt", "start"], [call["type"] for call in result["calls"]])
        self.assertEqual({"skipConfirmation": True}, result["calls"][1]["options"])


if __name__ == "__main__":
    unittest.main()
