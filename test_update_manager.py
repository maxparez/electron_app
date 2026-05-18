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


class UpdateManagerTests(unittest.TestCase):
    def test_check_for_update_compares_local_head_to_remote_channel(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const calls = [];
            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'windows-install', channel: 'stable' },
                execGit: (args) => {
                    calls.push(args);
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse' && args[1] === 'origin/windows-install') return 'remote-sha\\n';
                    if (args[0] === 'log') return '2026-05-15 [fix-158] Test update\\n';
                    return '';
                },
            });

            assert.deepStrictEqual(calls[0], ['fetch', 'origin', 'windows-install']);
            assert.strictEqual(result.updateAvailable, true);
            assert.strictEqual(result.localCommit, 'local-sha');
            assert.strictEqual(result.remoteCommit, 'remote-sha');
            assert.strictEqual(result.branch, 'windows-install');
            assert.strictEqual(result.channel, 'stable');
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertTrue(result["updateAvailable"])
        self.assertEqual("windows-install", result["branch"])

    def test_check_for_update_reports_current_installation(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'windows-install' },
                execGit: (args) => {
                    if (args[0] === 'rev-parse') return 'same-sha\\n';
                    if (args[0] === 'log') return '2026-05-15 [fix-158] Test update\\n';
                    return '';
                },
            });

            assert.strictEqual(result.updateAvailable, false);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertFalse(result["updateAvailable"])

    def test_start_update_requires_windows_and_update_script(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { startUpdate } = require('./src/electron/update-manager');

            const result = startUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                platform: 'linux',
                fileExists: () => true,
                spawnDetached: () => {
                    throw new Error('spawn should not be called');
                },
            });

            assert.strictEqual(result.success, false);
            assert.match(result.message, /Windows/);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertFalse(result["success"])

    def test_start_update_launches_batch_from_install_directory(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { startUpdate } = require('./src/electron/update-manager');

            let spawnCall = null;
            const result = startUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                platform: 'win32',
                fileExists: () => true,
                spawnDetached: (command, args, options) => {
                    spawnCall = { command, args, options };
                },
            });

            assert.strictEqual(result.success, true);
            assert.strictEqual(spawnCall.command, 'cmd.exe');
            assert.deepStrictEqual(spawnCall.args, ['/d', '/k', 'update-windows.bat']);
            assert.strictEqual(spawnCall.options.cwd, 'C:/OPJAK/electron_app');
            assert.strictEqual(spawnCall.options.detached, true);
            assert.strictEqual(spawnCall.options.windowsHide, false);
            process.stdout.write(JSON.stringify(spawnCall));
            """
        )

        result = run_node(script)

        self.assertEqual("cmd.exe", result["command"])


if __name__ == "__main__":
    unittest.main()
