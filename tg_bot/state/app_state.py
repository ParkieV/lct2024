from aiogram.fsm.state import StatesGroup, State


class AppState(StatesGroup):
    """
    Класс состояния приложения, где каждое состояние - это используемый handler на данный момент
    """
    login = State()  # шаг авторизации
    info = State()  # шаг информации о пользователе и о помощи
    help = State()  # шаг информации о пользователе и о помощи

    createNewPurchase = State()  # шаг создания новой закупки

    actionList = State()  # шаг общего списка действий
    product = State()  # шаг создания закупки
    commonPurchaseAnalysis = State()  # шаг общего анализа закупки
    balanceState = State()  # шаг баланса
    productAnalysis = State()  # шаг общего анализа товара
    activePurchase = State()  # шаг активных закупок
