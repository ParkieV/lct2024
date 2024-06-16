from aiogram.fsm.state import StatesGroup, State


class CreateNewPurchaseState(StatesGroup):
    """
    Класс для описания состояний в разделе <Создание новой закупки>
    """

    id = State()
    lotId = State()
    customerId = State()
