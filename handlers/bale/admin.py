import asyncio
import logging
import psutil

from aiogram import Router, types, Bot, F, filters, exceptions
from aiogram.utils import keyboard
from aiogram.fsm.context import FSMContext

from tortoise.exceptions import DoesNotExist

from db import Channel, BotInfo, User, RequiredJoinChats
from states import BotRequiredJoinChat, GlobalMessage
from utils.CustomGetChat import get_custom_chat


router = Router()
logger = logging.getLogger(__name__)

@router.message(filters.Command("admin"))
async def handle_admin(msg: types.Message, 
                          bot_info: BotInfo,
                          edit: bool=False):
    channel_count = await Channel.all().count()
    deleted_count = await Channel.filter(is_deleted=True).count()
    active_count = await Channel.filter(is_active=True, is_deleted=False).count()

    users_count = await User.all().count()

    txt = f"""*سلام رئیس☀️*

*اطلاعات دیتابیس:*
👥 تعداد کل کاربرا: {users_count}
📢 تعداد کل کانال ها: {channel_count}
🔪 کانال های حذف شده: {deleted_count}
⚒️ کانال های فعال: {active_count}
💎 تعداد فروارد های انجام شده: {bot_info.forwards}


*اطلاعات سرور:*
⚙️ CPU: {psutil.cpu_percent()} %
🪐 Ram: {psutil.virtual_memory().percent} %
📦 Storage: {psutil.disk_usage('/').percent} %"""
    

    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text=("🟢" if bot_info.is_active else "🔴") + "روشن / خاموش", callback_data="bot_active_toggle")
    builder.button(text="🏖 مدیریت کانال ها", callback_data="bot_manage_chats")
    builder.button(text="🪄 ارسال پیام عمومی", callback_data="bot_global_message")
    builder.adjust(1, 2)

    if edit:
        await msg.edit_text(txt, reply_markup=builder.as_markup())
    else:
        await msg.answer(txt, reply_markup=builder.as_markup())

@router.callback_query(F.data == "bot_active_toggle")
async def handle_bot_active_toggle(cb: types.CallbackQuery, 
                          bot_info: BotInfo):
    if not isinstance(cb.message, types.Message): return
    bot_info.is_active = not bot_info.is_active
    await bot_info.save()

    return await handle_admin(msg=cb.message, bot_info=bot_info, edit=True)


# Join required chats handlers
@router.callback_query(F.data == "bot_manage_chats")
async def handle_bot_manage_chats(cb: types.CallbackQuery,
                                  bale_bot: Bot,
                                  bot_info: BotInfo):
    if not isinstance(cb.message, types.Message): return
    
    chats = await RequiredJoinChats.filter(bot=bot_info)

    builder = keyboard.InlineKeyboardBuilder()
    for chat in chats:
        txt = None
        try:
            ch = await get_custom_chat(bale_bot, chat.channel_id)
            txt = ch.full_name
        except exceptions.TelegramAPIError:
            t = f"Bot is not admin in required chat: ID={chat.channel_id}, Username={chat.channel_username}"
            logger.error(t)
            await cb.message.answer(t)
        
        builder.button(text=txt or chat.channel_username or chat.channel_id, 
                       url=f"ble.ir/{chat.channel_username}" if chat.channel_username else "")
        builder.button(text="❌ حذف", callback_data=f"bot_delete_chat__{chat.id}")

    builder.button(text="➕ افزودن", callback_data=f"bot_add_chat")
    builder.adjust(*[2 for _ in range(len(chats))], 1)

    return await cb.message.edit_text(
        text="📂 مدیریت کانال ها:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("bot_delete_chat__"))
async def handle_bot_delete_chat(cb: types.CallbackQuery,
                                 state: FSMContext,
                                 bale_bot: Bot,
                                 bot_info: BotInfo):
    await state.clear()
    if not isinstance(cb.message, types.Message):
        return
    if cb.from_user is None or cb.data is None:
        logger.error("Invalid callback query from not user.")
        return

    chat_id = cb.data.split("__")[-1]
    try:
        required_chat = await RequiredJoinChats.get(id=int(chat_id), bot=bot_info)
        await required_chat.delete()
        await handle_bot_manage_chats(cb, bale_bot, bot_info)
    except DoesNotExist:
        return await cb.answer("🙁 این چت پیدا نشد...")
    except Exception as e:
        logger.error(f"{type(e)}: {e}")
        return await cb.answer("😭 یه مشکلی پیش اومد!")

@router.callback_query(F.data == "bot_add_chat")
async def handle_bot_add_chats(cb: types.CallbackQuery,
                                  state: FSMContext):
    await state.clear()
    if not isinstance(cb.message, types.Message): return
    if cb.from_user is None:
        logger.error("Invalid callback query from not user.")
        return

    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="🔙 بازگشت", callback_data="bot_manage_chats")
    txt = """این چت بله را به عنوان چت الزامی برای ربات اضافه کن.
آیدی عددی یا یوزرنیم چت را ارسال کن یا می‌توانی پیام آن را فوروارد کنی.

توجه کن که این چت برای بله است و باید ربات در آن ادمین باشد."""
    await state.set_state(BotRequiredJoinChat.bale_id)

    return await cb.message.edit_text(
        text=txt,
        reply_markup=builder.as_markup()
    )

@router.message(BotRequiredJoinChat.bale_id, F.text | F.forward_from_chat)
async def handle_bot_required_chat_id(
    msg: types.Message,
    state: FSMContext,
    bot_info: BotInfo
):
    if msg.from_user is None or msg.bot is None:
        logger.error("Invalid message from not user.")
        return

    if msg.forward_from_chat:
        chat_id = msg.forward_from_chat.id
    else:
        chat_id = msg.text or ''

    try:
        result = await msg.bot.get_chat_member(chat_id, msg.bot.id)
        if result.status != 'administrator':
            return await msg.reply(
                "❗ ربات در این چت دسترسی مدیرتی ندارد. ابتدا آن را به عنوان مدیر اضافه کن و دوباره تلاش کن.")

        chat = await get_custom_chat(msg.bot, chat_id)

        required_chat, created = await RequiredJoinChats.get_or_create(
            bot=bot_info,
            channel_id=str(chat.id),
            defaults={
                'channel_username': chat.username,
            }
        )

        if not created:
            if required_chat.channel_username != chat.username:
                required_chat.channel_username = chat.username
                await required_chat.save()
            await state.clear()
            return await msg.answer("✅ این چت قبلاً به لیست چت‌های الزامی اضافه شده بود.")

        await state.clear()
        return await msg.answer(
            f"✅ چت {chat.full_name} با موفقیت به لیست چت‌های الزامی اضافه شد."
        )

    except exceptions.TelegramAPIError as e:
        logger.error(f'{type(e)}: {e}')
        return await msg.reply(
            "❗ چت شناسایی نشد. لطفاً مطمئن شو ربات در چت ادمین است و شناسه یا لینک را درست ارسال کرده‌ای."
        )
    

# Global message handlers
@router.callback_query(F.data == "bot_global_message")
async def handle_bot_global_message(cb: types.CallbackQuery,
                                    state: FSMContext):
    await state.clear()
    if not isinstance(cb.message, types.Message):
        return
    if cb.from_user is None:
        logger.error("Invalid callback query from not user.")
        return

    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="🔙 بازگشت", callback_data="bot_manage_chats")
    await state.set_state(GlobalMessage.global_message)

    return await cb.message.edit_text(
        text="📢 پیامی که میخوای برا همه ارسال بشه رو بفرست:",
        reply_markup=builder.as_markup()
    )

@router.message(GlobalMessage.global_message)
async def handle_bot_global_message_text(
    msg: types.Message,
    state: FSMContext,
):
    if msg.from_user is None or msg.bot is None:
        logger.error("Invalid message from not user.")
        return

    users = await User.all().only('bale_id')
    target_count = len(users)
    await msg.answer(f"⏳ در حال ارسال پیام به {target_count} کاربر... لطفاً صبر کن.")

    sent = 0
    failed = 0

    for user in users:
        try:
            await msg.send_copy(user.bale_id)
            sent += 1
        except Exception as e:
            failed += 1
            logger.error(f"Global message failed for {user}: {type(e)} {e}")
        await asyncio.sleep(0.2)

    await state.clear()
    return await msg.answer(
        f"""✅ ارسال پیام کامل شد.
ارسال شده: {sent}
ناموفق: {failed}"""
)
