from aiogram.fsm.state import StatesGroup, State


class InfoState(StatesGroup):
    """
    Класс для описания состояний в разделе <Информация о пользователе и помощь>
    """
    userInfo = State()  # шаг информация о пользователе - сообщение об ошибке, выйти из аккаунта или вернуться назад
    assertError = State()  # шаг отправки сообщения об ошибке
