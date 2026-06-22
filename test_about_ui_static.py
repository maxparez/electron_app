#!/usr/bin/env python3

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


class AboutUiStaticTests(unittest.TestCase):
    def test_index_contains_about_navigation_and_section(self) -> None:
        html = (REPO_ROOT / "src" / "electron" / "renderer" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('data-tool="about"', html)
        self.assertIn("<span>O aplikaci</span>", html)
        self.assertIn('id="about-tool"', html)
        self.assertIn('id="about-current-version"', html)
        self.assertIn('id="about-channel"', html)
        self.assertIn('id="about-git"', html)
        self.assertIn('id="about-release-summary"', html)
        self.assertIn('id="about-release-changes"', html)
        self.assertIn("Historie změn", html)

    def test_preload_exposes_about_info_api(self) -> None:
        preload = (REPO_ROOT / "src" / "electron" / "preload.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("getAboutInfo", preload)
        self.assertIn("app:getAboutInfo", preload)

    def test_main_registers_about_info_handler(self) -> None:
        main = (REPO_ROOT / "src" / "electron" / "main.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("about-info", main)
        self.assertIn("app:getAboutInfo", main)

    def test_renderer_loads_and_renders_about_release_notes(self) -> None:
        renderer = (
            REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"
        ).read_text(encoding="utf-8")

        self.assertIn("aboutCurrentVersion", renderer)
        self.assertIn("loadAboutInfo", renderer)
        self.assertIn("renderAboutReleaseNotes", renderer)
        self.assertIn("renderAboutReleaseHistory", renderer)
        self.assertIn("info.releaseHistory", renderer)
        self.assertIn("about-release-version", renderer)
        self.assertIn("window.electronAPI.getAboutInfo", renderer)
        self.assertIn("about-release-empty", renderer)

    def test_styles_define_about_cards_with_update_dialog_language(self) -> None:
        styles = (
            REPO_ROOT / "src" / "electron" / "renderer" / "styles.css"
        ).read_text(encoding="utf-8")

        self.assertIn(".about-hero", styles)
        self.assertIn(".about-version-strip", styles)
        self.assertIn(".about-release-card", styles)
        self.assertIn(".about-release-version", styles)
        self.assertIn(".about-release-version-header", styles)
        self.assertIn(".about-release-empty", styles)


if __name__ == "__main__":
    unittest.main()
