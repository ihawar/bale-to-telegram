"""
These middleware adds the user to DB and update params.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from db import User


from setup_logger import setup_logger

logger = setup_logger(__name__)

class UserMiddleware(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject,
                                          Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:

        user, _ = await User.update_or_create(
            bale_id=str(event.event.from_user.id),
            defaults={'username': (event.event.from_user.username)}
        )
        data['user'] = user

        return await handler(event, data)
