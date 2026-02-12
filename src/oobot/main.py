"""Application entry point — CLI dispatcher and bot bootstrap.

Handles two execution modes:
  1. `oobot hook` — delegates to hook.hook_main() for OpenCode hook processing.
  2. Default — configures logging, initializes tmux session, and starts the
     Telegram bot polling loop via bot.create_bot().
"""

import logging
import sys

from telegram.error import NetworkError


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "hook":
        from .hook import hook_main

        hook_main()
        return

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.WARNING,
    )
    logging.getLogger("oobot").setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Import after logging is configured — Config() validates env vars
    from .config import config
    from .tmux_manager import tmux_manager

    logger.info("Allowed users: %s", config.allowed_users)
    logger.info("OpenCode projects path: %s", config.opencode_projects_path)
    logger.info("OpenCode storage path: %s", config.opencode_storage_path)

    # Ensure tmux session exists
    session = tmux_manager.get_or_create_session()
    logger.info("Tmux session '%s' ready", session.session_name)

    logger.info("Starting Telegram bot...")
    from .bot import create_bot

    application = create_bot()
    try:
        application.run_polling(allowed_updates=["message", "callback_query"])
    except NetworkError as e:
        logger.error("Telegram polling failed with network error: %s", e)
        logger.error(
            "Hint: check TELEGRAM_PROXY / TELEGRAM_TRUST_ENV. "
            "On macOS, system proxies may be auto-detected even when shell env vars are empty."
        )
        raise


if __name__ == "__main__":
    main()
