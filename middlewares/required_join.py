import logging

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, types, Bot
from aiogram.exceptions import TelegramNotFound
from aiogram.types import TelegramObject
from aiogram.utils import keyboard

from db import RequiredJoinChats, BotInfo


logger = logging.getLogger(__name__)

class JoinRequiredMiddleware(BaseMiddleware):
    async def __call__(self, 
                        handler: Callable[[TelegramObject, Dict[str, Any]], 
                        Awaitable[Any]], 
                        event: TelegramObject, 
                        data: Dict[str, Any]) -> Any:
        # ignore forwarder updates
        if isinstance(event.event, types.Message) and event.event.chat.type != 'private':
            return await handler(event, data)

        bot_info: BotInfo = data['bot_info']
        bale_bot: Bot = data['bale_bot']

        channels = await RequiredJoinChats.filter(bot=bot_info)
        not_joined_channels = []

        for channel in channels:
            try:
                await bale_bot.get_chat_member(chat_id=channel.channel_id, 
                                                    user_id=event.event.from_user.id)
            except TelegramNotFound:
                not_joined_channels.append(channel)
            except Exception as e:
                logger.error(e)
                await bale_bot.send_message(chat_id=bot_info.owner.bale_id,
                                             text=f"Error for required chat: link={channel.chat_link}\n {type(e)}: {e}")
    
        if not not_joined_channels:
            return await handler(event, data)


        msg = """شرمتده سلطان...👀

*برای استفاده از ربات لازمه عضو این چنتا کانال بشی(بعد دوباره /start رو بفرست):*
"""
        builder = keyboard.InlineKeyboardBuilder()
        for channel in not_joined_channels:
            builder.button(text=channel.channel_name, 
                           url=channel.chat_link)
        
        await bale_bot.send_message(
            chat_id=event.event.from_user.id,
            text=msg,
            reply_markup=builder.as_markup()
        )
        return
