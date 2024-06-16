from aiogram.fsm.state import StatesGroup, State


class AuthState(StatesGroup):
    """
    Класс для описания состояний в разделе <Авторизация>
    """
    login = State()  # Состояние ввода логина/почты
    password = State()  # Состояние ввода пароля
