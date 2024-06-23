from aiogram.fsm.state import StatesGroup, State


class ChoosePurchaseState(StatesGroup):
    """
    Класс для описания состояний в разделе <Выбор закупки>
    """

    choosePurchase = State()  # Состояние выбора активной закупки
    actionsList = State()  # Состояние отображения действий над закупкой
    chooseActionsFromList = State()  # Состояние выбора действия над закупкой
    editPurchase = State()  # Состояние редактирования закупки
