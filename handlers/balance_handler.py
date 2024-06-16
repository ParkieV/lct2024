"""
Раздел <Баланс>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from res.action_list_text import BALANCE_BUTTON_TEXT
from res.balance_text import *
from res.general_text import *
from state.app_state import AppState
from state.balance_state import BalanceState
from utils import isFloat

balanceRouter = Router()


@balanceRouter.message(default_state, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
@balanceRouter.message(AppState.actionList, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
@balanceRouter.message(AppState.balanceState, F.text == BALANCE_BUTTON_TEXT, flags={"rights": "balance"})
async def balanceInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.balanceState)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=INFO_BALANCE_BUTTON_TEXT),
        KeyboardButton(text=EDIT_BALANCE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=BALANCE_HELLO_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@balanceRouter.message(default_state, F.text == INFO_BALANCE_BUTTON_TEXT)
@balanceRouter.message(AppState.balanceState, F.text == INFO_BALANCE_BUTTON_TEXT)
async def infoBalance(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.balanceState)
    await message.answer(text=INFO_BALANCE_MESSAGE_TEXT)


@balanceRouter.message(default_state, F.text == EDIT_BALANCE_BUTTON_TEXT)
@balanceRouter.message(AppState.balanceState, F.text == EDIT_BALANCE_BUTTON_TEXT)
async def editBalanceAccount(message: Message, state: FSMContext) -> None:
    await state.set_state(BalanceState.editAccount)
    await message.answer(text=INPUT_BALANCE_ACCOUNT_MESSAGE_TEXT)


@balanceRouter.message(BalanceState.editAccount)
async def editBalanceSum(message: Message, state: FSMContext) -> None:
    accountNumber: str = message.text
    await state.update_data(accountNumber=accountNumber)
    print(accountNumber)

    await state.set_state(BalanceState.editBalance)
    await message.answer(text=INPUT_BALANCE_SUM_MESSAGE_TEXT)


@balanceRouter.message(BalanceState.editBalance)
async def completeEditBalance(message: Message, state: FSMContext) -> None:
    try:
        formattedBalanceSum: str = message.text.replace(",", ".")
        balanceSum: float | str = float(formattedBalanceSum) if isFloat(formattedBalanceSum) else formattedBalanceSum
        print(balanceSum)
        await state.update_data(balanceSum=balanceSum)

        await state.set_state(AppState.balanceState)

        print(await state.get_data())
        await balanceInit(message, state)
    except Exception as e:
        print(e)
        await message.answer(text=SOMETHING_WRONG)
