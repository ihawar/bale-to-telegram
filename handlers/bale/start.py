import logging

from aiogram import Router, types, Bot
from aiogram.utils import formatting, keyboard
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext


router = Router()
logger = logging.getLogger(__name__)



@router.message(CommandStart())
async def handle_start(msg: types.Message,
                       state: FSMContext,
                       bale_bot: Bot):
    return await restart_service(msg, state, bale_bot.id)


async def restart_service(msg: types.Message,
                       state: FSMContext,
                       bot_id: str | int,
                       edit: bool=False):
    await state.clear()
    if msg.from_user is None:
        logger.error("Invalid /start from not user.")
        return

    txt = formatting.Bold("🔗 کانال بله رو به کانال تلگرامت وصل کن!")
    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="📢 مدیریت کانال ها", callback_data="manage_channels")
    builder.button(text="➕ افزودن کانال", callback_data="add_channel")
    builder.button(text="☂️ راهنمایی", callback_data="help")

    builder.adjust(2, 1)
    
    logger.info("/start from (id={}, username={})."
                .format(msg.from_user.id | 0, msg.from_user.username)
                )
    if edit and msg.from_user.id == bot_id:
        return await msg.edit_text(
                    text=txt.as_markdown(),
                    reply_markup=builder.as_markup()
        )
    else:
        return await msg.reply(
            text=txt.as_markdown(),
            reply_markup=builder.as_markup()
        )

