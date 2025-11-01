import json
import logging
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Optional


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_API_BASE = "https://api.telegram.org"


def _get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Configure it in your Vercel project settings."
        )
    return token


def _call_telegram(method: str, payload: Dict[str, Any]) -> None:
    token = _get_token()
    url = f"{TELEGRAM_API_BASE}/bot{token}/{method}"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10):
            LOGGER.debug("Sent payload to %s", method)
    except urllib.error.HTTPError as exc:
        error_content = exc.read().decode("utf-8", errors="replace")
        LOGGER.warning("Telegram API responded with %s: %s", exc.code, error_content)
        raise
    except urllib.error.URLError as exc:
        LOGGER.error("Failed to reach Telegram API: %s", exc)
        raise


def _send_markdown(chat_id: int, text: str, reply_to: Optional[int]) -> bool:
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    if reply_to is not None:
        payload["reply_to_message_id"] = reply_to

    try:
        _call_telegram("sendMessage", payload)
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 400:
            return False
        raise


def _send_parse_error(chat_id: int, reply_to: Optional[int]) -> None:
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": (
            "I couldn't parse that Markdown. Please check your formatting "
            "and try again."
        ),
    }
    if reply_to is not None:
        payload["reply_to_message_id"] = reply_to

    _call_telegram("sendMessage", payload)


def _extract_message(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return update.get("message") or update.get("edited_message")


class handler(BaseHTTPRequestHandler):  # noqa: N801 (Vercel naming requirement)
    """Handle incoming webhook calls from Telegram."""

    def do_GET(self) -> None:  # type: ignore[override]
        self._send_response(200, {"status": "ok"})

    def do_POST(self) -> None:  # type: ignore[override]
        try:
            content_length = int(self.headers.get("content-length", "0"))
            body = self.rfile.read(content_length)
            update = json.loads(body or b"{}")
        except json.JSONDecodeError:
            LOGGER.warning("Received invalid JSON payload")
            self._send_response(400, {"error": "invalid_json"})
            return

        try:
            message = _extract_message(update)
            if not message:
                self._send_response(200, {"status": "ignored"})
                return

            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if chat_id is None:
                LOGGER.warning("No chat id in message: %s", message)
                self._send_response(200, {"status": "ignored"})
                return

            text = message.get("text")
            if not text:
                self._send_response(200, {"status": "ignored"})
                return

            reply_to = message.get("message_id")
            if _send_markdown(chat_id, text, reply_to):
                self._send_response(200, {"status": "sent"})
            else:
                _send_parse_error(chat_id, reply_to)
                self._send_response(200, {"status": "parse_error"})
        except RuntimeError as exc:
            LOGGER.error("Configuration error: %s", exc)
            self._send_response(500, {"error": "missing_token"})
        except Exception:
            LOGGER.exception("Unexpected error while handling update")
            self._send_response(500, {"error": "internal_error"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        LOGGER.info("%s - %s", self.address_string(), format % args)

    def _send_response(self, status: int, payload: Dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
