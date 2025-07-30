# tests/test_telegram_bot.py

import os
import pytest
import pytest_asyncio
from emrpy import TelegramTradingBot  # type: ignore

# Load environment variables (for local testing)
from dotenv import load_dotenv

load_dotenv()

# grab your real credentials
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or ""
CHAT_NAME = os.getenv("TELEGRAM_CHAT_NAME", "Trading Telegram Chat") or "Trading Telegram Chat"

# skip the entire module if credentials are missing
if not BOT_TOKEN or not CHAT_ID:
    pytest.skip(
        "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your environment to run Telegram integration tests",
        allow_module_level=True,
    )


@pytest_asyncio.fixture
async def real_bot():
    bot = TelegramTradingBot(bot_token=BOT_TOKEN, chat_id=CHAT_ID, chat_name=CHAT_NAME)
    yield bot
    # no teardown needed


@pytest.mark.asyncio
async def test_send_message_real(real_bot):
    """Should be able to send a simple text message."""
    ok = await real_bot.send_message("pytest → Hello from your real bot! 🐍")
    assert ok is True


@pytest.mark.asyncio
async def test_send_trade_alert_real(real_bot):
    """Should be able to send a formatted trade alert."""
    ok = await real_bot.send_trade_alert(
        symbol="PYTEST", action="BUY", price=123.45, quantity=1.0, profit_loss=10.0
    )
    assert ok is True


@pytest.mark.asyncio
async def test_send_bulk_notifications_real(real_bot):
    """Should be able to send a small bulk of messages."""
    msgs = [
        "pytest bulk → message 1",
        "pytest bulk → message 2",
        "pytest bulk → message 3",
    ]
    results = await real_bot.send_bulk_notifications(msgs)
    # expect a list of booleans, all True if everything worked
    assert isinstance(results, list)
    assert all(results), f"Some bulk messages failed: {results}"
