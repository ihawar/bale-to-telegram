"""
These middleware adds the Telegram and Bale bot object to updates.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from db import BotInfo


from setup_logger import setup_logger

logger = setup_logger(__name__)

class BotsMiddleware(BaseMiddleware):
    def __init__(self,
                 bot_info: BotInfo,
                 bale_bot: Bot,
                 tg_bot: Bot) -> None:
        self.bale_bot = bale_bot
        self.tg_bot = tg_bot
        self.bot_info = bot_info

        super().__init__()

    async def __call__(self,
                       handler: Callable[[TelegramObject,
                                          Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        data['bot_info'] = self.bot_info
        data['bale_bot'] = self.bale_bot
        data['tg_bot'] = self.tg_bot

        
        return await handler(event, data)
    