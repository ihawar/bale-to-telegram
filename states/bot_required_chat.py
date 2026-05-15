from aiogram.fsm.state import State, StatesGroup


class BotRequiredJoinChat(StatesGroup):
    bale_id = State()
