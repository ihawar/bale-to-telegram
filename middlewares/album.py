"""
These middleware is used for capturing media group updates.
"""
import asyncio
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types import TelegramObject


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.5):
        self.latency = latency
        self.album_data: Dict[str, List[Message]] = {}
        super().__init__()

    async def __call__(self,
                       handler: Callable[[TelegramObject,
                                          Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if not isinstance(event, Message): return

        if not event.media_group_id:
            return await handler(event, data)

        # Collect messages with the same media_group_id
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            
            data["album"] = self.album_data.pop(event.media_group_id)
            return await handler(event, data)
        else:
            self.album_data[event.media_group_id].append(event)
            return
