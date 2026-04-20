#!/usr/bin/env python3

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

from channel_config import ChannelConfig, config_for_branch, load_channel_config, resolve_debug_mode


class ChannelConfigTests(unittest.TestCase):
    def test_load_channel_config_uses_defaults_when_values_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "channel-config.json"
            config_path.write_text("{}", encoding="utf-8")

            config = load_channel_config(config_path)

            self.assertEqual("windows-install", config.branch)
            self.assertFalse(config.debug_logging)
            self.assertEqual("stable", config.channel)

    def test_load_channel_config_reads_explicit_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "channel-config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channel": "test",
                        "branch": "windows-install-test",
                        "debug_logging": True,
                    }
                ),
                encoding="utf-8",
            )

            config = load_channel_config(config_path)

            self.assertEqual("windows-install-test", config.branch)
            self.assertTrue(config.debug_logging)
            self.assertEqual("test", config.channel)

    def test_resolve_debug_mode_prefers_explicit_env_then_channel_debug(self) -> None:
        stable_config = ChannelConfig(channel="stable", branch="windows-install", debug_logging=False)
        test_config = ChannelConfig(channel="test", branch="windows-install-test", debug_logging=True)

        self.assertFalse(resolve_debug_mode(stable_config, {}))
        self.assertTrue(resolve_debug_mode(stable_config, {"FLASK_DEBUG": "true"}))
        self.assertFalse(resolve_debug_mode(test_config, {"FLASK_DEBUG": "false"}))

    def test_config_for_branch_returns_test_channel_for_windows_install_test(self) -> None:
        stable = config_for_branch("windows-install")
        test = config_for_branch("windows-install-test")

        self.assertEqual(ChannelConfig(channel="stable", branch="windows-install", debug_logging=False), stable)
        self.assertEqual(ChannelConfig(channel="test", branch="windows-install-test", debug_logging=True), test)


if __name__ == "__main__":
    unittest.main()
