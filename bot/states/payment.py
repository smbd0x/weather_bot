from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    waiting_for_amount = State()
