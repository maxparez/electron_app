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


class AboutInfoTests(unittest.TestCase):
    def test_read_about_info_combines_version_channel_release_notes_and_git(self) -> None:
        result = run_node(
            textwrap.dedent(
                """
                const assert = require('assert');
                const { readAboutInfo } = require('./src/electron/about-info');

                const info = readAboutInfo({
                    repoRoot: process.cwd(),
                    execGit: (args) => {
                        if (args.join(' ') === 'rev-parse --short HEAD') return 'abc1234\\n';
                        if (args.join(' ') === 'rev-parse --abbrev-ref HEAD') return 'windows-install\\n';
                        if (args.join(' ') === 'log -1 --format=%cd --date=short') return '2026-06-21\\n';
                        throw new Error(`Unexpected git call: ${args.join(' ')}`);
                    }
                });

                assert.strictEqual(info.version, '1.4.0');
                assert.strictEqual(info.channel.branch, 'windows-install');
                assert.strictEqual(info.channel.channel, 'stable');
                assert.strictEqual(info.git.commit, 'abc1234');
                assert.strictEqual(info.git.branch, 'windows-install');
                assert.strictEqual(info.git.date, '2026-06-21');
                assert.strictEqual(info.releaseNotes.version, '1.4.0');
                assert.ok(Array.isArray(info.releaseNotes.sections.features));
                assert.ok(
                    info.releaseNotes.sections.features.some(
                        (item) => item.title.includes('Rozdělení docházky')
                    )
                );

                process.stdout.write(JSON.stringify(info));
                """
            )
        )

        self.assertEqual("1.4.0", result["version"])
        self.assertEqual("windows-install", result["channel"]["branch"])
        self.assertEqual("stable", result["channel"]["channel"])

    def test_read_about_info_survives_missing_optional_files(self) -> None:
        result = run_node(
            textwrap.dedent(
                """
                const fs = require('fs');
                const os = require('os');
                const path = require('path');
                const assert = require('assert');
                const { readAboutInfo } = require('./src/electron/about-info');

                const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'about-info-'));
                fs.writeFileSync(
                    path.join(tempRoot, 'package.json'),
                    JSON.stringify({ name: 'test-app', version: '9.8.7' }),
                    'utf8'
                );

                const info = readAboutInfo({
                    repoRoot: tempRoot,
                    execGit: () => { throw new Error('git unavailable'); }
                });

                assert.strictEqual(info.version, '9.8.7');
                assert.strictEqual(info.channel.branch, 'windows-install');
                assert.strictEqual(info.releaseNotes, null);
                assert.strictEqual(info.git.commit, null);

                process.stdout.write(JSON.stringify(info));
                """
            )
        )

        self.assertEqual("9.8.7", result["version"])
        self.assertIsNone(result["releaseNotes"])
        self.assertIsNone(result["git"]["commit"])


if __name__ == "__main__":
    unittest.main()
