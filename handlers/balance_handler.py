"""
Раздел <Баланс>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import AsyncSessionDB
from db.db import User
from db.db_utils import getUser
from res.balance_text import *
from res.general_actions_text import BALANCE_BUTTON_TEXT
from res.general_text import *
from state.app_state import AppState
from state.balance_state import BalanceState

balanceRouter = Router()


@balanceRouter.message(default_state, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
@balanceRouter.message(AppState.generalActions, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
@balanceRouter.message(AppState.balance, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
async def balanceInit(message: Message, state: FSMContext) -> None:
    """
    Приветственное меню раздела <Баланс>
    """
    await state.set_state(AppState.balance)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=INFO_BALANCE_BUTTON_TEXT),
        KeyboardButton(text=EDIT_BALANCE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=BALANCE_HELLO_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@balanceRouter.message(default_state, F.text == INFO_BALANCE_BUTTON_TEXT)
@balanceRouter.message(AppState.balance, F.text == INFO_BALANCE_BUTTON_TEXT)
async def infoBalance(message: Message, state: FSMContext) -> None:
    """
    Информация о балансе стоимости закупок
    """
    await state.set_state(AppState.balance)

    user: User = await getUser(message.from_user.id)

    await message.answer(
        text=INFO_BALANCE_MESSAGE_TEXT(
            user.getAllPurchasesWithPrices(),
            user.balance
        )
    )


@balanceRouter.message(default_state, F.text == EDIT_BALANCE_BUTTON_TEXT)
@balanceRouter.message(AppState.balance, F.text == EDIT_BALANCE_BUTTON_TEXT)
async def editBalanceAccount(message: Message, state: FSMContext) -> None:
    """
    Начало редактирования баланса
    """
    await state.set_state(BalanceState.editBalance)
    await message.answer(text=INPUT_BALANCE_SUM_MESSAGE_TEXT)


@balanceRouter.message(BalanceState.editBalance)
async def completeEditBalance(message: Message, state: FSMContext) -> None:
    """
    Завершение редактирования баланса
    """

    try:
        balanceSum: int = int(message.text)

        async with AsyncSessionDB() as session:
            user: User = await getUser(message.from_user.id)
            await user.setBalance(balanceSum, session)

        await message.answer(text=SUCCESS_EDIT_BALANCE_TEXT)
        await balanceInit(message, state)
    except Exception as e:
        await message.answer(text=SOMETHING_WRONG)
