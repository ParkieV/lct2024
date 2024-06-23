from aiogram.fsm.state import StatesGroup, State


class CommonPurchaseAnalysisState(StatesGroup):
    """
    Класс для описания состояний в разделе <Общий анализ закупок>>
    """

    purchaseStatistics = State()
    expensivePurchase = State()
    choosePeriod = State()  # Состояние выбора периода для статистики по закупкам
    chooseStatisticType = State()  # Состояние выбора типа статистики по закупкам

    enterN = State()  # Состояние ввода N-количества для N самых дорогих закупок
