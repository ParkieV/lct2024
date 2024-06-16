from aiogram.fsm.state import StatesGroup, State


class BalanceState(StatesGroup):
    """
    Класс для описания состояний в разделе <Баланс>
    """

    editAccount = State()
    editBalance = State()
