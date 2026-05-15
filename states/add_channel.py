from aiogram.fsm.state import State, StatesGroup


class AddChannel(StatesGroup):
    bale_id = State()
    telegram_id = State()
