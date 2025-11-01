import { Bot, GrammyError, HttpError } from "grammy";
import type { Update } from "grammy/types";
import type { VercelRequest, VercelResponse } from "@vercel/node";

const token = process.env.TELEGRAM_BOT_TOKEN;

if (!token) {
  throw new Error(
    "TELEGRAM_BOT_TOKEN environment variable is not set. Configure it in Vercel before deploying."
  );
}

const bot = new Bot(token);

bot.catch(({ error }) => {
  console.error("Unexpected bot error", error);
});

let botInitPromise: Promise<void> | null = null;

async function ensureBotInitialized() {
  if (!botInitPromise) {
    botInitPromise = bot.init().catch((error) => {
      botInitPromise = null;
      throw error;
    });
  }

  await botInitPromise;
}

bot.command("start", async (ctx) => {
  await ctx.reply(
    "Send me a message that uses MarkdownV2 syntax and I'll respond with Telegram's rendered output."
  );
});

bot.on("message:text", async (ctx) => {
  const text = ctx.message.text ?? "";

  if (text.trim().length === 0) {
    return;
  }

  // Avoid re-processing commands that may slip through.
  if (text.startsWith("/")) {
    return;
  }

  try {
    await ctx.reply(text, {
      parse_mode: "MarkdownV2",
      link_preview_options: { is_disabled: true },
      reply_to_message_id: ctx.message.message_id,
    });
  } catch (error: unknown) {
    if (error instanceof GrammyError && error.error_code === 400) {
      await ctx.reply(
        "I couldn't parse that Markdown. Please check your formatting and try again.",
        {
          reply_to_message_id: ctx.message.message_id,
        }
      );
      return;
    }

    if (error instanceof HttpError) {
      console.error("Telegram HTTP error", error);
      throw error;
    }

    throw error;
  }
});

function parseUpdate(body: unknown): Update {
  if (!body) {
    throw new Error("Empty request body");
  }

  if (typeof body === "string") {
    return JSON.parse(body) as Update;
  }

  if (Buffer.isBuffer(body)) {
    return JSON.parse(body.toString("utf-8")) as Update;
  }

  return body as Update;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method === "GET") {
    res.status(200).json({ status: "ok" });
    return;
  }

  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    res.status(405).end("Method Not Allowed");
    return;
  }

  try {
    const update = parseUpdate(req.body);
    await ensureBotInitialized();
    await bot.handleUpdate(update);
    res.status(200).json({ status: "processed" });
  } catch (error) {
    console.error("Failed to process update", error);
    res.status(500).json({ error: "internal_error" });
  }
}
