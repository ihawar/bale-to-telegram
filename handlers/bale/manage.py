import logging

from aiogram import Bot, Router, types, F
from aiogram.utils import keyboard
from aiogram.fsm.context import FSMContext

from tortoise.exceptions import DoesNotExist

from handlers.bale.start import restart_service

from db import Channel, User

from utils import get_custom_chat

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "manage_channels")
async def handle_manage_channels(cb: types.CallbackQuery,
                       state: FSMContext, 
                       user: User, 
                       bale_bot: Bot, 
                       tg_bot: Bot):
    await state.clear()
    if not isinstance(cb.message, types.Message): return
    if cb.from_user is None:
        logger.error("Invalid callback query from not user.")
        return
    
    channels = await Channel.filter(owner=user, is_deleted=False)

    if len(channels) == 0:
        await cb.answer("😅 هنوز چنلی به ربات وصل نکردی")
        try:
            await restart_service(cb.message, state, bale_bot.id, edit=True)
        except:
            ...
        finally:
            return

    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="بله", callback_data="")
    builder.button(text="تلگرام", callback_data="")
    builder.button(text="فعال", callback_data="")
    builder.button(text="حذف", callback_data="")

    for ch in channels:
        builder.attach(await generate_channel_buttons(ch, bale_bot, tg_bot))

    builder.button(text="🔙 بازگشت", callback_data="cancel")
    builder.adjust(4, *[4 for _ in range(len(channels))], 1)
    return await cb.message.edit_text(
        "📂 مدیریت کانال های متصل شده:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("toggle_active__"))
async def handle_toggle_active(cb: types.CallbackQuery,
                       state: FSMContext, 
                       user: User, 
                       bale_bot: Bot, 
                       tg_bot: Bot):
    await state.clear()
    if not isinstance(cb.message, types.Message): return
    if cb.from_user is None or cb.data is None:
        logger.error("Invalid callback query from not user.")
        return
    
    ch_id = cb.data.split("__")[-1]
    try:
        ch_id = int(ch_id)
        channel = await Channel.get(owner=user, is_deleted=False, id=ch_id)
        channel.update_from_dict({"is_active": not channel.is_active})
        await channel.save()

        await handle_manage_channels(cb, state, user, bale_bot, tg_bot)
    except DoesNotExist:
        return await cb.answer("🙁 انگار این چنل پیدا نشد...")
    except Exception as e:
        logger.error(
            f"{type(e)}: {e}"
        )
        return await cb.answer("😭 یه مشکلی پیش اومد!")


@router.callback_query(F.data.startswith("delete__"))
async def handle_delete(cb: types.CallbackQuery,
                       state: FSMContext, 
                       user: User, 
                       bale_bot: Bot, 
                       tg_bot: Bot):
    await state.clear()
    if not isinstance(cb.message, types.Message): return
    if cb.from_user is None or cb.data is None:
        logger.error("Invalid callback query from not user.")
        return
    
    ch_id = cb.data.split("__")[-1]
    try:
        ch_id = int(ch_id)
        channel = await Channel.get(owner=user, is_deleted=False, id=ch_id)
        channel.update_from_dict({"is_deleted": True})
        await channel.save()

        await handle_manage_channels(cb, state, user, bale_bot, tg_bot)
    except DoesNotExist:
        return await cb.answer("🙁 انگار این چنل پیدا نشد...")
    except Exception as e:
        logger.error(
            f"{type(e)}: {e}"
        )
        return await cb.answer("😭 یه مشکلی پیش اومد!")


async def generate_channel_buttons(
        channel: Channel,
        bale_bot: Bot,
        tg_bot: Bot
):
    builder = keyboard.InlineKeyboardBuilder()
    
    bale_chat = await get_custom_chat(bale_bot, channel.bale_id)
    telegram_chat = await tg_bot.get_chat(channel.telegram_id)

    builder.button(text=bale_chat.full_name[:16], url=f"ble.ir/{bale_chat.username}" if bale_chat.username else "")
    builder.button(text=telegram_chat.full_name[:16], url=f"t.me/{telegram_chat.username}" if telegram_chat.username else "")
    builder.button(text="🟢" if channel.is_active else "🔴", callback_data=f"toggle_active__{channel.id}")
    builder.button(text="❌", callback_data=f"delete__{channel.id}")  
    
    return builder
