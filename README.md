# telegram-md

Telegram bot that receives a plain text message containing Markdown markup and replies with the formatted version.

## Prerequisites

- Python 3.11+
- A Telegram bot token (create one via [@BotFather](https://t.me/BotFather))

Install dependencies:

```
pip install -r requirements.txt
```

## Running the bot

Set the bot token as an environment variable and start the bot:

```
export TELEGRAM_BOT_TOKEN=your_token_here
python bot.py
```

Start a chat with your bot and send any message that uses Markdown syntax (for example, `**bold**` or `` `code` ``). The bot will reply with Markdown formatting applied.
