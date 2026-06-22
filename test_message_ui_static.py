#!/usr/bin/env python3

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


class MessageUiStaticTests(unittest.TestCase):
    def test_show_message_uses_fixed_body_container(self) -> None:
        renderer = (
            REPO_ROOT / "src" / "electron" / "renderer" / "renderer.js"
        ).read_text(encoding="utf-8")

        self.assertIn("function getMessageContainer", renderer)
        self.assertIn("message-container", renderer)
        self.assertIn("document.body.appendChild", renderer)
        self.assertIn("message.setAttribute('role', 'alert')", renderer)
        self.assertNotIn("content.insertBefore(message, content.firstChild)", renderer)

    def test_styles_keep_messages_visible_above_scrolled_content(self) -> None:
        styles = (
            REPO_ROOT / "src" / "electron" / "renderer" / "styles.css"
        ).read_text(encoding="utf-8")

        self.assertIn(".message-container", styles)
        self.assertIn("position: fixed", styles)
        self.assertIn("z-index: 3000", styles)
        self.assertIn(".message.warning", styles)


if __name__ == "__main__":
    unittest.main()
