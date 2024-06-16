"""
Раздел <Общий анализ закупок>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from res.action_list_text import COMMON_ANALYSIS_BUTTON_TEXT
from res.general_purchases_analysis_text import *
from res.info_text import *
from state.app_state import AppState

commonPurchasesAnalysisRouter = Router()


@commonPurchasesAnalysisRouter.message(default_state, F.text == COMMON_ANALYSIS_BUTTON_TEXT)
@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == COMMON_ANALYSIS_BUTTON_TEXT)
async def commonPurchaseAnalysisInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.commonPurchaseAnalysis)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=PURCHASES_STATISTIC_BUTTON_TEXT),
        KeyboardButton(text=TOP_EXPENSIVE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )
    print(await state.get_state())
    await message.answer(text=COMMON_PURCHASES_STATISTIC_HELLO_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@commonPurchasesAnalysisRouter.message(default_state, F.text == PURCHASES_STATISTIC_BUTTON_TEXT)
@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == PURCHASES_STATISTIC_BUTTON_TEXT)
async def purchaseStatistics(message: Message, state: FSMContext) -> None:
    # await state.set_state(CommonPurchaseAnalysisState.purchaseStatistics)
    await state.set_state(AppState.commonPurchaseAnalysis)
    await message.answer(text=PURCHASES_STATISTIC_MESSAGE_TEXT)


@commonPurchasesAnalysisRouter.message(default_state, F.text == TOP_EXPENSIVE_BUTTON_TEXT)
@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == TOP_EXPENSIVE_BUTTON_TEXT)
async def purchaseStatistics(message: Message, state: FSMContext) -> None:
    # await state.set_state(CommonPurchaseAnalysisState.expensivePurchase)
    await state.set_state(AppState.commonPurchaseAnalysis)
    await message.answer(text=TOP_EXPENSIVE_MESSAGE_TEXT)
