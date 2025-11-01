#!/usr/bin/env node

const { TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL } = process.env;

function fail(message) {
  console.error(message);
  process.exit(1);
}

function parseArgs() {
  const args = process.argv.slice(2);
  let url = TELEGRAM_WEBHOOK_URL;
  let dropPending = false;
  let mode = "set";

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];

    if (arg === "--drop") {
      mode = "delete";
      continue;
    }

    if (arg === "--drop-pending-updates") {
      dropPending = true;
      continue;
    }

    if (arg === "--url") {
      if (i + 1 >= args.length) {
        fail("Missing value for --url");
      }
      url = args[i + 1];
      i += 1;
      continue;
    }

    if (arg.startsWith("--url=")) {
      url = arg.slice("--url=".length);
      continue;
    }

    fail(`Unknown argument: ${arg}`);
  }

  return { mode, url, dropPending };
}

async function callTelegram(endpoint, body) {
  const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/${endpoint}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok || !data || !data.ok) {
    const description = data?.description ?? response.statusText;
    fail(`Telegram API call failed: ${description}`);
  }

  return data;
}

async function main() {
  if (!TELEGRAM_BOT_TOKEN) {
    fail("Set TELEGRAM_BOT_TOKEN in your environment before running this script.");
  }

  const { mode, url, dropPending } = parseArgs();

  if (mode === "set" && !url) {
    fail("Provide the webhook URL via --url or TELEGRAM_WEBHOOK_URL environment variable.");
  }

  if (mode === "set") {
    try {
      new URL(url);
    } catch (error) {
      fail(`Invalid webhook URL: ${error instanceof Error ? error.message : String(error)}`);
    }

    console.log(`Setting webhook to ${url}`);
    await callTelegram("setWebhook", {
      url,
      drop_pending_updates: dropPending,
      allowed_updates: [],
    });
    console.log("Webhook registered successfully.");
    return;
  }

  console.log("Deleting webhook");
  await callTelegram("deleteWebhook", {
    drop_pending_updates: dropPending,
  });
  console.log("Webhook deleted successfully.");
}

main().catch((error) => {
  if (error instanceof Error) {
    fail(error.message);
    return;
  }

  fail(String(error));
});
