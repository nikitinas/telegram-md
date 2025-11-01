# telegram-md

Serverless Telegram bot written in TypeScript using [grammY](https://grammy.dev/). It receives a message containing MarkdownV2 markup and replies with the rendered version when deployed on [Vercel](https://vercel.com/).

## How it works

- `api/webhook.ts` exposes a serverless webhook handler backed by grammY.
- On every incoming update, the bot reposts the message using `parse_mode=MarkdownV2`.
- If Telegram reports a MarkdownV2 parsing error, the bot sends a friendly error response instead of crashing.

## Deploy to Vercel

1. **Create a Telegram bot** via [@BotFather](https://t.me/BotFather) and copy the API token.
2. **Set up environment variables** in Vercel: go to *Project Settings ? Environment Variables* and define `TELEGRAM_BOT_TOKEN` with your bot token.
3. **Install dependencies** locally (optional but recommended for testing):
   ```
   npm install
   ```
4. **Deploy** the project (e.g., `vercel --prod`). Vercel automatically builds and exposes the function at `/api/webhook` using the Node.js runtime.
5. **Register the webhook** once deployment finishes by running the helper script (replace the URL with your deployment):
   ```
   TELEGRAM_BOT_TOKEN=<YOUR_TOKEN> npm run set-webhook -- --url https://<your-project>.vercel.app/api/webhook
   ```
   - You can export `TELEGRAM_BOT_TOKEN` once in your shell instead of prefixing the command every time.
   - Set `TELEGRAM_WEBHOOK_URL` in your environment to skip the `--url` flag.
   - Pass `--drop` to remove the webhook, or `--drop-pending-updates` to ask Telegram to discard queued updates while registering or deleting the webhook.
6. **Test** by messaging your bot. MarkdownV2 snippets such as `*bold*`, `_italic_`, or `` `code` `` should render correctly. If the Telegram client auto-formats your message, escape the special characters (e.g., send `\*bold\*`).

## Local testing (optional)

Vercel CLI can emulate the webhook handler locally:

```
vercel dev
```

Then expose the local server with a tunneling tool (e.g., [ngrok](https://ngrok.com/)) and call `setWebhook` with the public URL for end-to-end testing. Ensure `TELEGRAM_BOT_TOKEN` is exported in your shell before running `vercel dev` so the local function can call Telegram.
