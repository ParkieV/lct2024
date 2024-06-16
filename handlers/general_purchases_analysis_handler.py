"""
Раздел <Общий анализ закупок>
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db.db import User
from db.db_utils import getUser
from res.action_list_text import COMMON_ANALYSIS_BUTTON_TEXT
from res.general_purchases_analysis_text import *
from res.general_text import *
from state.app_state import AppState
from state.general_purchase_analysis_state import CommonPurchaseAnalysisState

commonPurchasesAnalysisRouter = Router()


@commonPurchasesAnalysisRouter.message(default_state, F.text == COMMON_ANALYSIS_BUTTON_TEXT,
                                       flags={"rights": "analysis_common"})
@commonPurchasesAnalysisRouter.message(AppState.actionList, F.text == COMMON_ANALYSIS_BUTTON_TEXT,
                                       flags={"rights": "analysis_common"})
@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == COMMON_ANALYSIS_BUTTON_TEXT,
                                       flags={"rights": "analysis_common"})
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


@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == PURCHASES_STATISTIC_BUTTON_TEXT)
async def purchaseStatistics(message: Message, state: FSMContext) -> None:
    # await state.set_state(CommonPurchaseAnalysisState.purchaseStatistics)
    await state.set_state(AppState.commonPurchaseAnalysis)
    await message.answer(text=PURCHASES_STATISTIC_MESSAGE_TEXT)


@commonPurchasesAnalysisRouter.message(AppState.commonPurchaseAnalysis, F.text == TOP_EXPENSIVE_BUTTON_TEXT)
async def suggestProduct(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=YEAR_TEXT),
        KeyboardButton(text=QUARTER_TEXT),
        KeyboardButton(text=MONTH_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(CommonPurchaseAnalysisState.choosePeriod)
    await message.answer(text=CHOSE_PERIOD_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@commonPurchasesAnalysisRouter.message(CommonPurchaseAnalysisState.choosePeriod, F.text == YEAR_TEXT)
@commonPurchasesAnalysisRouter.message(CommonPurchaseAnalysisState.choosePeriod, F.text == QUARTER_TEXT)
@commonPurchasesAnalysisRouter.message(CommonPurchaseAnalysisState.choosePeriod, F.text == MONTH_TEXT)
async def suggestProductYear(message: Message, state: FSMContext) -> None:
    await state.set_state(CommonPurchaseAnalysisState.chooseStatisticType)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=AMOUNT_OF_PURCHASES_BUTTON_TEXT),
        KeyboardButton(text=PRICE_OF_PURCHASES_BUTTON_TEXT),
    )

    period: int = 0
    if message.text == YEAR_TEXT:
        period = 1
    elif message.text == QUARTER_TEXT:
        period = 2
    elif message.text == MONTH_TEXT:
        period = 3

    await state.update_data(сommonPurchaseAnalysis_period=period)
    await message.answer(text=SELECT_PERIOD_TEXT(period), reply_markup=keyboard.as_markup(resize_keyboard=True))


@commonPurchasesAnalysisRouter.message(CommonPurchaseAnalysisState.chooseStatisticType,
                                       F.text == AMOUNT_OF_PURCHASES_BUTTON_TEXT)
async def suggestProductYear(message: Message, state: FSMContext) -> None:
    user: User = await getUser(message.chat.id)
    # async with aiohttp.ClientSession(cookies=user.cookies) as session:
    #     async with session.post(f"{"http://localhost:8080"}/api/auth/refresh") as response:
    #         pass
    # if response.status != 200:

    # user.setCookies(response.cookies)
    # await self.session.commit()


@commonPurchasesAnalysisRouter.message(CommonPurchaseAnalysisState.chooseStatisticType,
                                       F.text == PRICE_OF_PURCHASES_BUTTON_TEXT)
async def suggestProductYear(message: Message, state: FSMContext) -> None:
    user: User = await getUser(message.chat.id)
