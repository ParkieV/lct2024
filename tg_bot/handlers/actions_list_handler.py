"""
Раздел <Общий список действий>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.active_purchase import activePurchaseInit
from handlers.balance_handler import balanceInit
from handlers.general_purchases_analysis_handler import commonPurchaseAnalysisInit
from handlers.product_handler import productInit
from res.action_list_text import *
from res.info_text import *
from state.app_state import AppState

actionListRouter = Router()


@actionListRouter.message(default_state, F.text == CONTINUE_BUTTON_TEXT)
@actionListRouter.message(AppState.info, F.text == CONTINUE_BUTTON_TEXT)
@actionListRouter.message(AppState.actionList, F.text == CONTINUE_BUTTON_TEXT)
async def actionListHandlerInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.actionList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=ENTER_PRODUCT_NAME_BUTTON_TEXT),
        KeyboardButton(text=ACTIVE_PURCHASE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=COMMON_ANALYSIS_BUTTON_TEXT),
        KeyboardButton(text=BALANCE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=ACTION_LIST_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@actionListRouter.message(default_state, F.text == COMMON_ANALYSIS_BUTTON_TEXT)
@actionListRouter.message(AppState.actionList, F.text == COMMON_ANALYSIS_BUTTON_TEXT)
async def commonAnalysisGoTo(message: Message, state: FSMContext) -> None:
    await commonPurchaseAnalysisInit(message, state)


@actionListRouter.message(default_state, F.text == BALANCE_BUTTON_TEXT)
@actionListRouter.message(AppState.actionList, F.text == BALANCE_BUTTON_TEXT)
async def balanceGoTo(message: Message, state: FSMContext) -> None:
    await balanceInit(message, state)


@actionListRouter.message(default_state, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
@actionListRouter.message(AppState.actionList, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
async def productGoTo(message: Message, state: FSMContext) -> None:
    await productInit(message, state)


@actionListRouter.message(AppState.actionList, F.text == ACTIVE_PURCHASE_BUTTON_TEXT)
async def activePurchaseGoTo(message: Message, state: FSMContext) -> None:
    await activePurchaseInit(message, state)
