import logging
import os
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


LOGGER = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a short how-to message when the user issues /start."""
    await update.message.reply_text(
        "Send me a message that contains Markdown markup and I will reply "
        "with the formatted version."
    )


async def format_markdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the incoming message while asking Telegram to render Markdown."""
    if not update.message or not update.message.text:
        return

    message_text = update.message.text

    try:
        await update.message.reply_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except BadRequest as exc:
        LOGGER.warning("Failed to render Markdown: %s", exc)
        await update.message.reply_text(
            "I couldn't parse that Markdown. Please check your formatting and try again.",
        )


def get_bot_token() -> str:
    token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Provide your bot token before running the bot."
        )
    return token


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = get_bot_token()

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, format_markdown))

    LOGGER.info("Bot started. Waiting for messages...")
    application.run_polling()


if __name__ == "__main__":
    main()
