from aiogram.fsm.state import StatesGroup, State

class AllPath(StatesGroup):
    """FSM states for user interaction."""
    registration = State()
    choosing_option = State()
    input_dislike = State()
    input_like = State()
    post = State()
    change_payment = State()