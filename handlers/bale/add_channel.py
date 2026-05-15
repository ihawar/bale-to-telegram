import logging

from aiogram import Bot, Router, types, F, exceptions
from aiogram.utils import formatting, keyboard
from aiogram.fsm.context import FSMContext

from states import AddChannel

from db import Channel, User

from utils import get_custom_chat

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "add_channel")
async def handle_add_channel(cb: types.CallbackQuery,
                       state: FSMContext,
                       user: User):
    await state.clear()
    if not isinstance(cb.message, types.Message): return
    if cb.from_user is None:
        logger.error("Invalid callback query from not user.")
        return
    
    # MAXIMUM NUMBER OF CHANNELS PER USER 2
    if len(await Channel.filter(owner=user, is_deleted=False)) >= 2:
            await state.clear()
            return await cb.message.answer("""🙃 بیشتر از این نمیتونی به ربات کانال وصل کنی...
                      
درحال حاضر بیشترین تعداد کانال های متصل برای هر کاربر ۲ عدد است.
در آینده این محدودیت رفع میشود.""")
    
    await state.set_state(AddChannel.bale_id)

    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="🔙 بازگشت", callback_data="cancel")
    txt = """این ربات رو به کانال بله اضافه کن و *آیدی عددی* یا *یوزرنیم کانالت* رو اینجا ارسال کن. حتی میتونی یه پیام از کانالت فروارد کنی تا ربات خودکار تشخیصش بده😇

📌 برای اضافه کردن ربات، توی کانالت در *قسمت مدیران* روی *افزودن مدیر جدید* بزنید و اسم ربات رو سرچ کنید و به کانال تون اضافه ش کنید(لازم نیست هیچ دسترسی خاصی به ربات بدین)"""
    
    logger.info(f"New \"Add channel request\" from (id={cb.from_user.id}, username={cb.from_user.username})")
    return await cb.message.edit_text(
        text=txt,
        reply_markup=builder.as_markup()
    )


@router.message(AddChannel.bale_id, F.text | F.forward_from_chat)
async def handle_bale_id(
    msg: types.Message,
    state: FSMContext
):
    if msg.from_user is None or msg.bot is None:
        logger.error("Invalid message from not user.")
        return
    
    # Get the chat_id from the forwarded chat or message text
    if msg.forward_from_chat:
        chat_id = msg.forward_from_chat.id
    else:
        chat_id = msg.text or ''

    try:
        result = await msg.bot.get_chat_member(chat_id, msg.bot.id)
        if result.status != 'administrator':
            return await msg.reply(
            "❗ ربات در کانال دسترسی های لازم را ندارد. از قسمت افزودن مدیر ربات را اضافه کنید و دوباره تلاش کنید.")
        

        chat = await get_custom_chat(msg.bot, chat_id)
        await state.update_data(
            bale_id=chat.id,
            bale_username=chat.username,
            bale_name=chat.full_name
        )

        await state.set_state(AddChannel.telegram_id)

        builder = keyboard.InlineKeyboardBuilder()
        builder.button(text="🔙 بازگشت", callback_data="cancel")
        return await msg.reply(
            """✅ چنل بله افزوده شد.

حالا ربات تلگرام رو توی تلگرام به آیدی @beleTGBot پیدا کنید و اون رو داخل چنل تلگرام تون ادمین کنید و یوزرنیم یا آیدی عددی کانال تلگرام رو اینجا ارسال کنید:
"""
        , reply_markup=builder.as_markup())
        
    except exceptions.TelegramAPIError as e:
        logger.error(
            f'{type(e)}: {e.message}'
        )
        return await msg.reply(
            """❗ کانال شناسایی نشد.
ابتدا مطمئن شوید ربات در کانال مدیر است سپس مطمئن شوید آیدی ارسال شده صحیح است."""
        )

@router.message(AddChannel.telegram_id, F.text)
async def handle_telegram_id(
    msg: types.Message,
    state: FSMContext,
    tg_bot: Bot,
    user: User
):
    if msg.from_user is None or msg.bot is None:
        logger.error("Invalid message from not user.")
        return
    
    chat_id = msg.text or ''
    try:
        result = await tg_bot.get_chat_member(chat_id, tg_bot.id)
        if result.status != 'administrator':
            return await msg.reply(
            "❗ بات در کانال دسترسی های لازم را ندارد. آن را به صورت ادمین اضافه کنید.")
        
        chat = await tg_bot.get_chat(chat_id)
        await state.update_data(
            telegram_id=chat.id,
            telegram_username=chat.username,
            telegram_name=chat.full_name
        )

        ch, created = await Channel.get_or_create(
            bale_id=str(await state.get_value('bale_id')),
            bale_username=await state.get_value('bale_username'),
            telegram_id=str(await state.get_value('telegram_id')),
            telegram_username=await state.get_value('telegram_username'),
            owner=user,
            is_deleted=False
        )
        if not created:
            return await msg.reply("✅ چنل قبلا توسط شما افزوده شده بود.")

        txt = """*تمام👀*
✅ از امروز هر پستی که در کانال {bale_name} بله ارسال شود توسط ربات در تلگرام {telegram_name} نیز منتشر میشود.
""".format(
            bale_name=formatting.Bold(await state.get_value('bale_name')).as_markdown(),
            telegram_name=formatting.Bold(await state.get_value('telegram_name')).as_markdown(),
        )

        await state.clear()
        logger.info(
            f"New Channel added by (id={msg.from_user.id}, username={msg.from_user.username})\n" +
            f"Bale: (username: {ch.bale_username}), Telegram: (username: {ch.telegram_username})"
        )
        return await msg.answer(txt)
    
    except exceptions.TelegramAPIError as e:
        logger.error(
            f'{type(e)}: {e.message}'
        )
        return await msg.reply(
            """❗ کانال شناسایی نشد.
ابتدا مطمئن شوید ربات در کانال مدیر است سپس مطمئن شوید آیدی ارسال شده صحیح است."""
        )
