"""
Раздел <Аналитика по товару>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from res.general_text import BACK_BUTTON_TEXT
from res.product_analysis_text import *
from res.product_text import ANALYZE_PRODUCT_BUTTON_TEXT
from state.app_state import AppState
from state.product_state import ProductState

productAnalysisRouter = Router()


@productAnalysisRouter.message(ProductState.productWaitActions, F.text == ANALYZE_PRODUCT_BUTTON_TEXT,
                               flags={"rights": "analysis_product"})
@productAnalysisRouter.message(AppState.productAnalysis, F.text == ANALYZE_PRODUCT_BUTTON_TEXT,
                               flags={"rights": "analysis_product"})
async def productAnalysisInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.productAnalysis)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=HOW_MANY_ITEMS_LEFT_BUTTON_TEXT),
        KeyboardButton(text=LAST_N_PURCHASE_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=DEBIT_CREDIT_PRODUCT_BUTTON_TEXT),
        KeyboardButton(text=STATISTIC_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=PRODUCT_ANALYSIS_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == HOW_MANY_ITEMS_LEFT_BUTTON_TEXT)
async def howManyItemsLeft(message: Message, state: FSMContext) -> None:
    productName: str = (await state.get_data())['productName']
    await message.answer(text=HOW_MANY_ITEMS_LEFT_MESSAGE_TEXT(productName))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == LAST_N_PURCHASE_BUTTON_TEXT)
async def lastNPurchase(message: Message, state: FSMContext) -> None:
    await message.answer(text=LAST_N_PURCHASE_MESSAGE_TEXT)


@productAnalysisRouter.message(AppState.productAnalysis, F.text == DEBIT_CREDIT_PRODUCT_BUTTON_TEXT)
async def debitCreditProduct(message: Message, state: FSMContext) -> None:
    productName: str = (await state.get_data())['productName']
    await message.answer(text=DEBIT_CREDIT_PRODUCT_MESSAGE_TEXT(productName))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == STATISTIC_BUTTON_TEXT)
async def statisticProduct(message: Message, state: FSMContext) -> None:
    productName: str = (await state.get_data())['productName']
    await message.answer(text=STATISTIC_MESSAGE_TEXT(productName))
