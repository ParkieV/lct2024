"""
Раздел <Информация о пользователе и помощь>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db.db_utils import logout
from handlers.actions_list_handler import actionListHandlerInit
from res.general_text import SOMETHING_WRONG, BACK_BUTTON_TEXT
from res.info_text import *
from res.login_text import TRANSITION_BUTTON_TEXT
from state.app_state import AppState
from state.info_state import InfoState

infoRouter = Router()


@infoRouter.message(AppState.info, F.text == TRANSITION_BUTTON_TEXT)
async def infoHandlerInit(message: Message, state: FSMContext) -> None:
    """
    Функция-инициализатор для раздела <Информация о пользователе и помощь>.
    Создает навигационные кнопки
    :param message:
    :param state:
    """
    await state.set_state(AppState.info, )

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=CONTINUE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=EXIT_BUTTON_TEXT),
        KeyboardButton(text=HELP_BUTTON_TEXT)
    )
    await message.answer(text=INFO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@infoRouter.message(default_state, F.text == HELP_BUTTON_TEXT)
@infoRouter.message(AppState.info, F.text == HELP_BUTTON_TEXT)
async def getHelp(message: Message, state: FSMContext) -> None:
    """
    Функция, которая выводит справочную информацию при нажатии на кнопку {HELP_BUTTON_TEXT}.
    :param message:
    :param state:
    :return:
    """

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=ASSERT_BUTTON_TEXT),
        KeyboardButton(text=BACK_BUTTON_TEXT),
    )

    await state.set_state(InfoState.userInfo)
    await message.reply(text=HELP_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@infoRouter.message(default_state, F.text == ASSERT_BUTTON_TEXT)
@infoRouter.message(InfoState.userInfo, F.text == ASSERT_BUTTON_TEXT)
async def assertError(message: Message, state: FSMContext) -> None:
    """
    Функция, которая позволяет отправить сообщение об ошибке.
    Запрашивает ввести текстом сообщение
    :param message:
    :param state:
    :return:
    """
    await state.set_state(InfoState.assertError)
    await message.answer(text=ASSERT_MESSAGE_TEXT)


@infoRouter.message(InfoState.assertError)
async def sendAssertedError(message: Message, state: FSMContext) -> None:
    """
    Функция, которая отправляет введенное сообщение об ошибке.
    :param message:
    :param state:
    :return:
    """
    print(message.text)
    await state.set_state(AppState.info)
    await message.reply(text=ASSERT_MESSAGE_SUCCESS)
    await infoHandlerInit(message, state)


@infoRouter.message(default_state, F.text == EXIT_BUTTON_TEXT)
@infoRouter.message(InfoState.userInfo, F.text == EXIT_BUTTON_TEXT)
@infoRouter.message(AppState.info, F.text == EXIT_BUTTON_TEXT)
async def exitFromAccount(message: Message, state: FSMContext) -> None:
    """
    Функция, которая позволяет выйти из аккаунта.
    :param message:
    :param state:
    :return:
    """
    isSuccessLogout: bool = await logout(message.chat.id)
    if isSuccessLogout:
        await message.answer(text=EXIT_SUCCESS_TEXT, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(text=SOMETHING_WRONG)


@infoRouter.message(default_state, F.text == CONTINUE_BUTTON_TEXT)
@infoRouter.message(AppState.info, F.text == CONTINUE_BUTTON_TEXT)
async def continueAction(message: Message, state: FSMContext) -> None:
    """
    Функция для перехода к следующему разделу <Общий список действий>.
    :param message:
    :param state:
    :return:
    """
    await state.set_state(AppState.actionList)
    await actionListHandlerInit(message, state)
