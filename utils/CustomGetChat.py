from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from aiogram import types, Bot
from aiogram.methods import TelegramMethod



async def get_custom_chat(bot: Bot, chat_id: types.ChatIdUnion) -> CustomChatFullInfo:
    return await bot.session.make_request(
            bot=bot,
            method=CustomGetChat(chat_id=chat_id),
        )


class CustomChatFullInfo(BaseModel):
    """Chat model for your custom API (Bale)"""
    id: int
    type: str 
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo: Optional[types.ChatPhoto] = None
    bio: Optional[str] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    linked_chat_id: Optional[int] = None  
    
    accent_color_id: Optional[int] = Field(default=0)
    max_reaction_count: Optional[int] = Field(default=0)

    @property
    def full_name(self) -> str:
        """Get full name of the Chat.

        For private chat it is first_name + last_name.
        For other chat types it is title.
        """
        if self.title is not None:
            return self.title

        if self.last_name is not None:
            return f"{self.first_name} {self.last_name}"

        return f"{self.first_name}"


class CustomGetChat(TelegramMethod[CustomChatFullInfo]):
    """
    Use this method to get up-to-date information about the chat. Returns a :class:`aiogram.types.chat_full_info.ChatFullInfo` object on success.

    Source: https://core.telegram.org/bots/api#getchat
    """

    __returning__ = CustomChatFullInfo
    __api_method__ = "getChat"

    chat_id: types.ChatIdUnion
    """Unique identifier for the target chat or username of the target supergroup or channel (in the format :code:`@channelusername`)"""

    if TYPE_CHECKING:
        # DO NOT EDIT MANUALLY!!!
        # This section was auto-generated via `butcher`

        def __init__(
            __pydantic__self__, *, chat_id: types.ChatIdUnion, **__pydantic_kwargs: Any
        ) -> None:
            # DO NOT EDIT MANUALLY!!!
            # This method was auto-generated via `butcher`
            # Is needed only for type checking and IDE support without any additional plugins

            super().__init__(chat_id=chat_id, **__pydantic_kwargs)
