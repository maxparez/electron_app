from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_BRANCH = "windows-install"
DEFAULT_CHANNEL = "stable"


@dataclass(frozen=True)
class ChannelConfig:
    channel: str = DEFAULT_CHANNEL
    branch: str = DEFAULT_BRANCH
    debug_logging: bool = False


def get_default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "channel-config.json"


def load_channel_config(config_path: str | Path | None = None) -> ChannelConfig:
    resolved_path = Path(config_path) if config_path else get_default_config_path()
    if not resolved_path.exists():
        return ChannelConfig()

    raw_data = json.loads(resolved_path.read_text(encoding="utf-8"))
    return ChannelConfig(
        channel=str(raw_data.get("channel") or DEFAULT_CHANNEL),
        branch=str(raw_data.get("branch") or DEFAULT_BRANCH),
        debug_logging=bool(raw_data.get("debug_logging", False)),
    )


def resolve_debug_mode(config: ChannelConfig, env: dict[str, str] | None = None) -> bool:
    environment = env or {}
    if "FLASK_DEBUG" in environment:
        return str(environment["FLASK_DEBUG"]).strip().lower() == "true"
    return config.debug_logging


def config_for_branch(branch: str) -> ChannelConfig:
    normalized = str(branch).strip()
    if normalized == "windows-install-test":
        return ChannelConfig(channel="test", branch="windows-install-test", debug_logging=True)
    if normalized == "windows-install":
        return ChannelConfig(channel="stable", branch="windows-install", debug_logging=False)
    return ChannelConfig(branch=normalized or DEFAULT_BRANCH)


def write_channel_config_for_branch(branch: str, destination: str | Path | None = None) -> Path:
    target = Path(destination) if destination else get_default_config_path()
    config = config_for_branch(branch)
    target.write_text(
        json.dumps(
            {
                "channel": config.channel,
                "branch": config.branch,
                "debug_logging": config.debug_logging,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return target


if __name__ == "__main__":
    branch = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BRANCH
    destination = sys.argv[2] if len(sys.argv) > 2 else None
    write_channel_config_for_branch(branch, destination)
