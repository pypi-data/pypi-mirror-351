"""
Telegram Trading Bot Module

A lightweight, async-first Telegram bot client optimized for trading notifications.
Built on top of python-telegram-bot library for reliability and ease of use.
"""

import asyncio
import logging
from typing import Optional, List
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Configure logging
logger = logging.getLogger(__name__)


class TelegramTradingBot:
    """
    Lightweight Telegram bot for trading notifications.

    Features:
    - Async-first design for minimal latency impact
    - Simple message sending
    - Formatted trade alerts
    - Bulk notifications support
    - Built-in error handling and logging
    """

    def __init__(self, bot_token: str, chat_id: str, chat_name: Optional[str] = None):
        """
        Initialize the Telegram bot.

        Args:
            bot_token: Your Telegram bot token from @BotFather
            chat_id: Target chat ID (can be user ID or group chat ID)
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.chat_name = chat_name or chat_id  # Use chat_id as fallback name

    async def send_message(
        self, text: str, parse_mode: Optional[str] = None, disable_notification: bool = False
    ) -> bool:
        """
        Send a text message to the configured chat.

        Args:
            text: Message text to send
            parse_mode: 'HTML' or 'Markdown' for formatting (optional)
            disable_notification: Send silently without notification sound

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
            )
            logger.debug(f"Message sent successfully to {self.chat_name}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send message to {self.chat_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    async def send_trade_alert(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        profit_loss: Optional[float] = None,
        disable_notification: bool = False,
    ) -> bool:
        """
        Send a formatted trade alert with emoji and structured layout.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSD', 'AAPL')
            action: Trade action ('BUY', 'SELL', 'CLOSE')
            price: Execution price
            quantity: Trade quantity/size
            profit_loss: P/L amount (optional, will show emoji based on sign)
            disable_notification: Send silently without notification sound

        Returns:
            bool: True if alert sent successfully, False otherwise
        """
        # Choose emoji based on action and P/L
        if profit_loss is not None:
            pl_text = f"<b>P/L:</b> ${profit_loss:+.2f}"
            emoji = "📈" if profit_loss >= 0 else "📉"
        else:
            pl_text = ""
            if action.upper() == "BUY":
                emoji = "🟢"
            elif action.upper() == "SELL":
                emoji = "🔴"
            else:
                emoji = "💰"

        # Format the trade alert message
        message = f"""
                    {emoji} <b>TRADE ALERT</b>
                    <b>Symbol:</b> {symbol}
                    <b>Action:</b> {action.upper()}
                    <b>Price:</b> ${price:.4f}
                    <b>Quantity:</b> {quantity}
                    {pl_text}
                            """.strip()

        return await self.send_message(
            text=message, parse_mode=ParseMode.HTML, disable_notification=disable_notification
        )

    async def send_bulk_notifications(
        self,
        messages: List[str],
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
    ) -> List[bool]:
        """
        Send multiple messages concurrently for better performance.

        Args:
            messages: List of message texts to send
            parse_mode: 'HTML' or 'Markdown' for formatting (optional)
            disable_notification: Send silently without notification sound

        Returns:
            List[bool]: List of success status for each message
        """
        if not messages:
            logger.warning("Empty message list provided to send_bulk_notifications")
            return []

        # Create tasks for concurrent execution
        tasks = [self.send_message(msg, parse_mode, disable_notification) for msg in messages]

        try:
            # Execute all messages concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to False, keep boolean results
            success_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Bulk message {i} failed: {result}")
                    success_results.append(False)
                else:
                    success_results.append(result)

            logger.info(
                f"Bulk notifications: {sum(success_results)}/{len(messages)} sent successfully"
            )
            return success_results

        except Exception as e:
            logger.error(f"Unexpected error in bulk notifications: {e}")
            return [False] * len(messages)
