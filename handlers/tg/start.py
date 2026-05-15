from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils import keyboard

router = Router()

@router.message(CommandStart())
async def handle_start(msg: types.Message):
    if not msg.bot: return

    txt = """درود سلطان!🫀

اینجا کاری نداریم،‌ هرچیزی که لازم داری توی ربات بله هست.

آیدی ربات بله: `@baleTGBot`"""

    me = await msg.bot.get_me()
    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="➕ افزودن ربات به کانال",
                   url=f"t.me/{me.username}?startchannel&admin=post_messages")
    await msg.answer(txt, reply_markup=builder.as_markup())
