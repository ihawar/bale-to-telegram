import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


from db import BotInfo, User

logger = logging.getLogger(__name__)
class AdminMiddleware(BaseMiddleware):
    async def __call__(self, 
                        handler: Callable[[TelegramObject, 
                        Dict[str, Any]], Awaitable[Any]], 
                        event: TelegramObject, 
                        data: Dict[str, Any]) -> Any:
        bot_info: BotInfo = data['bot_info']
        user: User = data['user']

        if user.bale_id != bot_info.owner.bale_id:
            logger.warning(f"Unauthorized request denied by user {user.bale_id} ({user.username})")
            return
        

        return await handler(event, data)
    