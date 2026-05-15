from aiogram.fsm.state import State, StatesGroup


class GlobalMessage(StatesGroup):
    global_message = State()
