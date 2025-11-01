# telegram-md

Serverless Telegram bot that receives a message containing Markdown markup and replies with the rendered version. Designed for deployment on [Vercel](https://vercel.com/).

## How it works

- `api/webhook.py` exposes a webhook endpoint compatible with Vercel?s Python runtime.
- On every incoming update, the bot reposts the message using `parse_mode=Markdown`.
- If Telegram reports a Markdown parsing error, the bot sends a friendly error response instead of crashing.

## Deploy to Vercel

1. **Create a Telegram bot** via [@BotFather](https://t.me/BotFather) and copy the API token.
2. **Set up environment variables** in Vercel: go to *Project Settings ? Environment Variables* and define `TELEGRAM_BOT_TOKEN` with your bot token.
3. **Deploy** the project (e.g., `vercel --prod`). Vercel automatically builds and exposes the function at `/api/webhook`.
4. **Register the webhook** once deployment finishes:
   ```
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-project>.vercel.app/api/webhook"
   ```
5. **Test** by messaging your bot. Markdown snippets such as `**bold**`, `_italic_`, or `` `code` `` should render correctly.

## Local testing (optional)

Vercel CLI can emulate the webhook handler locally:

```
vercel dev
```

Then expose the local server with a tunneling tool (e.g., [ngrok](https://ngrok.com/)) and call `setWebhook` with the public URL for end-to-end testing.
