import logging

from aiogram import Router, Bot
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from .start import restart_service


router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "cancel")
async def handle_cancel(cb: types.CallbackQuery,
                       state: FSMContext,
                       bale_bot: Bot):
    if not isinstance(cb.message, types.Message): return
    return await restart_service(cb.message, state, bale_bot.id, edit=True)
