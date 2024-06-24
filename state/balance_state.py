from aiogram.fsm.state import StatesGroup, State


class BalanceState(StatesGroup):
    """
    Класс для описания состояний в разделе <Баланс>
    """

    editBalance = State()
