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
    def test_check_for_update_prefers_checked_out_branch_over_stale_config(self) -> None:
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
                    if (args.join(' ') === 'branch --show-current') {
                        return 'feat-171-split-attendance\\n';
                    }
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse') return 'remote-sha\\n';
                    if (args[0] === 'show' && args[1] === 'HEAD:package.json') {
                        return JSON.stringify({ version: '1.4.0' });
                    }
                    if (args[0] === 'show' && args[1] === 'origin/feat-171-split-attendance:package.json') {
                        return JSON.stringify({ version: '1.4.0' });
                    }
                    if (args[0] === 'show') throw new Error('notes missing');
                    if (args[0] === 'log') return 'remote-sha 2026-06-21 [fix] Test build\\n';
                    return '';
                },
            });

            assert.strictEqual(result.branch, 'feat-171-split-attendance');
            assert.strictEqual(result.channel, 'test');
            assert.deepStrictEqual(calls[1], ['fetch', 'origin', 'feat-171-split-attendance']);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertEqual("feat-171-split-attendance", result["branch"])
        self.assertEqual("test", result["channel"])

    def test_check_for_update_never_offers_older_remote_version(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'windows-install', channel: 'stable' },
                execGit: (args) => {
                    if (args.join(' ') === 'branch --show-current') return 'windows-install\\n';
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse') return 'older-remote-sha\\n';
                    if (args[0] === 'show' && args[1] === 'HEAD:package.json') {
                        return JSON.stringify({ version: '1.4.0' });
                    }
                    if (args[0] === 'show' && args[1] === 'origin/windows-install:package.json') {
                        return JSON.stringify({ version: '1.3.0' });
                    }
                    if (args[0] === 'show') throw new Error('notes missing');
                    if (args[0] === 'log') return 'older 2026-06-19 [release] Old\\n';
                    return '';
                },
            });

            assert.strictEqual(result.updateAvailable, false);
            assert.strictEqual(result.downgradeBlocked, true);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertFalse(result["updateAvailable"])
        self.assertTrue(result["downgradeBlocked"])

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

            assert.deepStrictEqual(calls[0], ['branch', '--show-current']);
            assert.deepStrictEqual(calls[1], ['fetch', 'origin', 'windows-install']);
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

    def test_check_for_update_returns_remote_version_and_release_notes(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const releaseNotes = {
                version: '1.4.0',
                date: '2026-06-21',
                summary: 'Nové nástroje a přehlednější aktualizace.',
                sections: {
                    features: [{
                        title: 'Rozdělení docházky',
                        description: 'Sešit lze rozdělit podle listů.'
                    }],
                    improvements: [],
                    fixes: []
                }
            };

            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'windows-install', channel: 'stable' },
                execGit: (args) => {
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse') return 'remote-sha\\n';
                    if (args[0] === 'show' && args[1] === 'HEAD:package.json') {
                        return JSON.stringify({ version: '1.3.0' });
                    }
                    if (args[0] === 'show' && args[1] === 'origin/windows-install:package.json') {
                        return JSON.stringify({ version: '1.4.0' });
                    }
                    if (args[0] === 'show' && args[1] === 'origin/windows-install:release-notes.json') {
                        return JSON.stringify(releaseNotes);
                    }
                    if (args[0] === 'log') return 'remote-sha 2026-06-21 [release] Sync\\n';
                    return '';
                },
            });

            assert.strictEqual(result.currentVersion, '1.3.0');
            assert.strictEqual(result.latestVersion, '1.4.0');
            assert.deepStrictEqual(result.releaseNotes, releaseNotes);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertEqual("1.3.0", result["currentVersion"])
        self.assertEqual("1.4.0", result["latestVersion"])
        self.assertEqual(
            "Rozdělení docházky",
            result["releaseNotes"]["sections"]["features"][0]["title"],
        )

    def test_check_for_update_falls_back_when_release_notes_are_missing(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'legacy-branch', channel: 'test' },
                execGit: (args) => {
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse') return 'remote-sha\\n';
                    if (args[0] === 'show') throw new Error('path does not exist');
                    if (args[0] === 'log') return 'remote-sha 2026-06-21 [fix] Legacy update\\n';
                    return '';
                },
            });

            assert.strictEqual(result.releaseNotes, null);
            assert.strictEqual(result.latestVersion, null);
            assert.match(result.latestSummary, /Legacy update/);
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertIsNone(result["releaseNotes"])
        self.assertIn("Legacy update", result["latestSummary"])

    def test_check_for_update_does_not_reuse_notes_for_same_version(self) -> None:
        script = textwrap.dedent(
            """
            const assert = require('assert');
            const { checkForUpdate } = require('./src/electron/update-manager');

            const result = checkForUpdate({
                repoRoot: 'C:/OPJAK/electron_app',
                channelConfig: { branch: 'windows-install-test', channel: 'test' },
                execGit: (args) => {
                    if (args[0] === 'rev-parse' && args[1] === 'HEAD') return 'local-sha\\n';
                    if (args[0] === 'rev-parse') return 'remote-sha\\n';
                    if (args[0] === 'show' && args[1] === 'HEAD:package.json') {
                        return JSON.stringify({ version: '1.4.0' });
                    }
                    if (args[0] === 'show') {
                        return JSON.stringify({
                            version: '1.4.0',
                            sections: { features: [{ title: 'Old', description: 'Old' }] }
                        });
                    }
                    if (args[0] === 'log') return 'remote-sha 2026-06-22 [fix] Test build\\n';
                    return '';
                },
            });

            assert.strictEqual(result.releaseNotes, null);
            assert.strictEqual(result.latestVersion, '1.4.0');
            process.stdout.write(JSON.stringify(result));
            """
        )

        result = run_node(script)

        self.assertIsNone(result["releaseNotes"])
        self.assertEqual("1.4.0", result["latestVersion"])

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
