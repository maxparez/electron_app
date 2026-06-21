#!/usr/bin/env python3

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def run_node(script: str, cwd: Path = REPO_ROOT):
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return json.loads(completed.stdout)


class ReleaseManagerTests(unittest.TestCase):
    def test_selects_semver_bump_from_change_fragments(self) -> None:
        result = run_node(
            textwrap.dedent(
                """
                const release = require('./scripts/release-manager');
                process.stdout.write(JSON.stringify({
                    fix: release.determineReleaseType([{ type: 'fix' }]),
                    feature: release.determineReleaseType([{ type: 'fix' }, { type: 'feature' }]),
                    breaking: release.determineReleaseType([{ type: 'feature', breaking: true }]),
                    override: release.determineReleaseType([{ type: 'feature' }], 'patch'),
                    next: release.bumpVersion('1.3.9', 'minor')
                }));
                """
            )
        )

        self.assertEqual("patch", result["fix"])
        self.assertEqual("minor", result["feature"])
        self.assertEqual("major", result["breaking"])
        self.assertEqual("patch", result["override"])
        self.assertEqual("1.4.0", result["next"])

    def test_prepare_release_updates_versions_and_generates_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "changes").mkdir()
            (root / "config").mkdir()
            (root / "src" / "electron").mkdir(parents=True)

            package = {"name": "test-app", "version": "1.3.0"}
            lock = {
                "name": "test-app",
                "version": "1.3.0",
                "lockfileVersion": 3,
                "packages": {"": {"name": "test-app", "version": "1.3.0"}},
            }
            (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
            (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
            (root / "config" / "production.json").write_text(
                json.dumps({"app": {"version": "1.3.0"}}),
                encoding="utf-8",
            )
            (root / "config" / "development.json").write_text(
                json.dumps({"app": {"version": "1.3.0-dev"}}),
                encoding="utf-8",
            )
            (root / "src" / "electron" / "config.js").write_text(
                'version: "1.3.0",\n',
                encoding="utf-8",
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\nPůvodní obsah\n",
                encoding="utf-8",
            )
            (root / "changes" / "splitter.json").write_text(
                json.dumps(
                    {
                        "type": "feature",
                        "title": "Rozdělení docházky",
                        "description": "Sloučený sešit lze rozdělit podle listů.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "changes" / "updater.json").write_text(
                json.dumps(
                    {
                        "type": "improvement",
                        "title": "Přehled aktualizací",
                        "description": "Aktualizace zobrazí podrobné změny.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            module_path = json.dumps(
                str(REPO_ROOT / "scripts" / "release-manager.js")
            )
            root_path = json.dumps(str(root))
            result = run_node(
                textwrap.dedent(
                    f"""
                    const release = require({module_path});
                    const result = release.prepareRelease({{
                        rootDir: {root_path},
                        date: '2026-06-21'
                    }});
                    process.stdout.write(JSON.stringify(result));
                    """
                ),
                cwd=root,
            )

            self.assertEqual("1.4.0", result["version"])
            self.assertEqual("minor", result["releaseType"])
            self.assertEqual("1.4.0", json.loads((root / "package.json").read_text())["version"])
            self.assertEqual(
                "1.4.0",
                json.loads((root / "package-lock.json").read_text())["packages"][""]["version"],
            )
            self.assertEqual(
                "1.4.0-dev",
                json.loads((root / "config" / "development.json").read_text())["app"]["version"],
            )
            self.assertIn(
                'version: "1.4.0"',
                (root / "src" / "electron" / "config.js").read_text(),
            )

            notes = json.loads((root / "release-notes.json").read_text(encoding="utf-8"))
            self.assertEqual("1.4.0", notes["version"])
            self.assertEqual(
                "Verze 1.4.0: 1 nová funkce a 1 vylepšení.",
                notes["summary"],
            )
            self.assertEqual("Rozdělení docházky", notes["sections"]["features"][0]["title"])
            self.assertEqual(
                "Přehled aktualizací",
                notes["sections"]["improvements"][0]["title"],
            )

            changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn("## [1.4.0] - 2026-06-21", changelog)
            self.assertIn("### Nové funkce", changelog)
            self.assertIn("**Rozdělení docházky**", changelog)
            self.assertIn("Původní obsah", changelog)
            self.assertEqual([], list((root / "changes").glob("*.json")))

    def test_prepare_release_rejects_empty_change_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "changes").mkdir()
            (root / "package.json").write_text(
                json.dumps({"version": "1.3.0"}),
                encoding="utf-8",
            )
            module_path = json.dumps(
                str(REPO_ROOT / "scripts" / "release-manager.js")
            )
            root_path = json.dumps(str(root))

            completed = subprocess.run(
                [
                    "node",
                    "-e",
                    textwrap.dedent(
                        f"""
                        const release = require({module_path});
                        try {{
                            release.prepareRelease({{ rootDir: {root_path} }});
                        }} catch (error) {{
                            process.stdout.write(error.message);
                            process.exit(2);
                        }}
                        """
                    ),
                ],
                capture_output=True,
                text=True,
                cwd=root,
            )

            self.assertEqual(2, completed.returncode)
            self.assertIn("Žádné change fragmenty", completed.stdout)


if __name__ == "__main__":
    unittest.main()
