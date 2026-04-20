#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

import server
from channel_config import ChannelConfig


class ServerMetadataTests(unittest.TestCase):
    def test_build_backend_metadata_reflects_current_identity(self) -> None:
        with patch.object(server, "CHANNEL_CONFIG", ChannelConfig(channel="test", branch="windows-install-test", debug_logging=True)):
            with patch.object(server, "BACKEND_INSTANCE_TOKEN", "instance-123"):
                with patch.object(server, "BACKEND_PORT", 5050):
                    metadata = server.build_backend_metadata()

        self.assertEqual("test", metadata["channel"])
        self.assertEqual("windows-install-test", metadata["branch"])
        self.assertTrue(metadata["debugLogging"])
        self.assertEqual("instance-123", metadata["instanceToken"])
        self.assertEqual(5050, metadata["port"])
        self.assertIn("pid", metadata)

    def test_health_endpoint_exposes_backend_identity(self) -> None:
        with patch.object(server, "CHANNEL_CONFIG", ChannelConfig(channel="stable", branch="windows-install", debug_logging=False)):
            with patch.object(server, "BACKEND_INSTANCE_TOKEN", "health-token"):
                with patch.object(server, "BACKEND_PORT", 5000):
                    response = server.app.test_client().get("/api/health")

        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertEqual("healthy", payload["status"])
        self.assertEqual("windows-install", payload["branch"])
        self.assertEqual("stable", payload["channel"])
        self.assertEqual("health-token", payload["instanceToken"])


if __name__ == "__main__":
    unittest.main()
