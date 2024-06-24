from aiogram.fsm.state import StatesGroup, State


class ProductState(StatesGroup):
    """
    Класс для описания состояний в разделе <Товар>
    """
    initActions = State()

    # Ввод имени товара и его выбор
    productName = State()
    productNameSuggestedList = State()
    enterProductNumFromList = State()

    # Выбор действия над товаром
    productActions = State()
    productWaitActions = State()
    productAnalysis = State()
    productSuggestion = State()
    productPurchase = State()

    predictChoosePeriod = State()
    predictChooseType = State()

    # Создание закупки с заказом
    waitPurchaseActions = State()
    cretePurchase = State()
    inputSubAccount = State()

    # Анализ товара
    productStatistic = State()
    productStatisticChoosePeriod = State()
    productDebitCredit = State()
    enterLastNProducts = State()
