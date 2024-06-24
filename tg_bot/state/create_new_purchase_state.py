from aiogram.fsm.state import StatesGroup, State


class CreateNewPurchaseState(StatesGroup):
    """
    Класс для описания состояний в разделе <Создание новой закупки>
    """

    id = State()  # состояние ввода идентификатора закупки
    lotId = State()  # состояние ввода идентификатора лота
    customerId = State()  # состояние ввода идентификатора клиента
