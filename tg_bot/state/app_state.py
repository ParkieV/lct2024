from aiogram.fsm.state import StatesGroup, State


class AppState(StatesGroup):
    """
    Класс состояния приложения, где каждое состояние - это используемый handler на данный момент
    """
    login = State()  # шаг авторизации
    info = State()  # шаг информации о пользователе и о помощи

    createPurchase = State()  # шаг создания новой закупки

    generalActions = State()  # шаг общего списка действий
    commonPurchaseAnalysis = State()  # шаг общего анализа закупки
    balance = State()  # шаг баланса
    productAnalysis = State()  # шаг общего анализа товара
    activePurchase = State()  # шаг активных закупок
