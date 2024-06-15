from aiogram.fsm.state import StatesGroup, State


class ProductState(StatesGroup):
    """
    Класс для описания состояний в разделе <Товар>
    """
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

    choosePeriod = State()

    # Создание закупки с заказом
    waitPurchaseActions = State()
    cretePurchase = State()
    inputSubAccount = State()
