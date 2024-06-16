from aiogram.fsm.state import StatesGroup, State


class CommonPurchaseAnalysisState(StatesGroup):
    """
    Класс для описания состояний в разделе <Общий анализ закупок>>
    """
    waitPressButtons = State()
    purchaseStatistics = State()
    expensivePurchase = State()
    choosePeriod = State()
    chooseStatisticType = State()
