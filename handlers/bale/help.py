from aiogram import Router, types, F
from aiogram.utils import keyboard

from config import config

router = Router()

@router.callback_query(F.data == "help")
async def handle_start(cb: types.CallbackQuery):
    if not isinstance(cb.message, types.Message):
        return
    
    txt = f"""این ربات برای کمک به کسانی طراحی شده است که در تلگرام کانال دارن.
 شما ربات رو به کانال تلگرام تون وصل میکنید و ربات پست هایی که میخواید رو اونجا براتون میزاره.🫶

*روش کار به این شکله که یک کانال بله میسازید و حالا ربات رو هم به کانال بله و هم به کانال تلگرام وصل میکنید. حالا هر پستی که در کانال بله بفرستید(عکس، ویدیو، ویس،‌ فایل هرچی) دقیقا به همون شکل در کانال تلگرام تون ارسال میشه.*🚀

📌 نکته ۱: شما نیاز دارید ربات رو هم در *کانال بله* و هم در *کانال تلگرام* به صورت *ادمین(مدیر)* اضافه کنید. لازم نیس دسترسی خاصی به ربات بدین فقط کافیه ربات دسترسی لازم برای *خوندن پیام های بله و ارسال پیام در تلگرام* داشته باشد.

📌 نکته ۲: آیدی ربات در تلگرام @baleTGBot میباشد و باید اون ربات رو داخل کانال تلگرام تون اضافه کنید.


اگر به راهنمایی نیاز داشتید میتونید به آیدی {config['BALE']['SUPPORT_ID']} پیام بدین.
به امید آزادی اینترنت❤️"""
    
    builder = keyboard.InlineKeyboardBuilder()
    builder.button(text="🔙 بازگشت", callback_data="cancel")

    await cb.message.edit_text(text=txt, reply_markup=builder.as_markup())
