"""Application configuration — reads env vars and exposes a singleton.

Loads TELEGRAM_BOT_TOKEN, ALLOWED_USERS, tmux/OpenCode paths, and
monitoring intervals from environment variables (with .env support).
Config directory defaults to ./.oobot, overridable via OOBOT_DIR.
The .env file is loaded from the current project directory (cwd).
The module-level `config` instance is imported by nearly every other module.

Key class: Config (singleton instantiated as `config`).
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from .utils import oobot_dir

logger = logging.getLogger(__name__)


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        # Load .env from current project directory (cwd)
        env_file = Path.cwd() / ".env"
        if env_file.is_file():
            load_dotenv(env_file, override=True)
            logger.debug("Loaded env from %s", env_file)
        else:
            logger.debug("No .env found at %s", env_file)

        self.config_dir = oobot_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN") or ""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        allowed_users_str = os.getenv("ALLOWED_USERS", "")
        if not allowed_users_str:
            raise ValueError("ALLOWED_USERS environment variable is required")
        try:
            self.allowed_users: set[int] = {
                int(uid.strip()) for uid in allowed_users_str.split(",") if uid.strip()
            }
        except ValueError as e:
            raise ValueError(
                f"ALLOWED_USERS contains non-numeric value: {e}. "
                "Expected comma-separated Telegram user IDs."
            ) from e

        # Tmux session name and window naming
        self.tmux_session_name = os.getenv("TMUX_SESSION_NAME", "oobot")
        self.tmux_main_window_name = "__main__"

        # OpenCode command to run in new windows
        self.opencode_command = os.getenv("OPENCODE_COMMAND", "opencode")

        # All state files live under config_dir
        self.state_file = self.config_dir / "state.json"
        self.session_map_file = self.config_dir / "session_map.json"
        self.monitor_state_file = self.config_dir / "monitor_state.json"

        # OpenCode session monitoring configuration (storage + legacy projects)
        self.opencode_projects_path = Path(
            os.getenv(
                "OPENCODE_PROJECTS_PATH", str(Path.home() / ".opencode" / "projects")
            )
        ).expanduser()
        self.opencode_storage_path = Path(
            os.getenv(
                "OPENCODE_STORAGE_PATH",
                str(Path.home() / ".local" / "share" / "opencode" / "storage"),
            )
        ).expanduser()
        self.monitor_poll_interval = float(os.getenv("MONITOR_POLL_INTERVAL", "2.0"))

        # Display user messages in history and real-time notifications
        # When True, user messages are shown with a 👤 prefix
        self.show_user_messages = True

        logger.debug(
            "Config initialized: dir=%s, token=%s..., allowed_users=%d, "
            "tmux_session=%s",
            self.config_dir,
            self.telegram_bot_token[:8],
            len(self.allowed_users),
            self.tmux_session_name,
        )

    def is_user_allowed(self, user_id: int) -> bool:
        """Check if a user is in the allowed list."""
        return user_id in self.allowed_users


config = Config()
