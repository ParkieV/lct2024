from aiogram.fsm.state import StatesGroup, State


class ActivePurchaseState(StatesGroup):
    """
    Класс для описания состояний в разделе <Активные закупки>
    """
    purchaseList = State()  # Состояние выбора активной закупки
    choosePurchase = State()  # Состояние выбора активной закупки
    actionsList = State()  # Состояние выбора активной закупки
    editPurchase = State()  # Состояние ввода пароля
