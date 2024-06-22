"""
Раздел <Аналитика по товару>
"""
import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import apiURL, bot, apiURL_ML
from db.db import User
from db.db_utils import getUserCookies, getUser
from res.general_purchases_analysis_text import AMOUNT_OF_PURCHASES_BUTTON_TEXT, PRICE_OF_PURCHASES_BUTTON_TEXT
from res.general_text import *
from res.product_analysis_text import *
from res.product_text import ANALYZE_PRODUCT_BUTTON_TEXT
from state.app_state import AppState
from state.product_state import ProductState
from utils import base64ToBufferInputStream


class ProductAnalysisActions(object):
    @staticmethod
    async def debitCredit(message, credit: bool) -> bytes:
        async with aiohttp.ClientSession(cookies=await getUserCookies(message.chat.id)) as session:
            async with session.get(f"{apiURL}/search/debit_credit_info", params={
                "credit": str(credit)
            }) as r:
                res = await r.json()

                if res['state'] != 'Success':
                    return b''

                return base64ToBufferInputStream(res['plot_image'])

    @staticmethod
    async def pickProduct(message, product_name: str):
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.post(f"{apiURL}/search/set_user_pick", params={
                "user_pick": product_name,
                "user_id": user.db_id
            }) as r:
                print(await r.json())

        async with aiohttp.ClientSession(headers={
            'accept': 'application/json',
        }) as session:
            async with session.post(f"{apiURL_ML}/v1/ml/matching/set_user_pick/", params={
                "user_id": user.db_id,
                "user_pick": product_name
            }) as r:
                print(await r.json())

    @staticmethod
    async def lastNPurchase(message, n) -> bytes:
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.get(f"{apiURL_ML}/v1/ml/analytics/history", params={
                "user_id": user.db_id,
                "n": str(n),
            }) as r:
                res = await r.json()
                return base64ToBufferInputStream(res['file'])

    @staticmethod
    async def statisticPurchase(message, period, price: bool) -> bytes:
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.get(f"{apiURL_ML}/v1/ml/analytics/purchase_stats", params={
                "period": period,
                "user_id": user.db_id,
                "summa": str(price),
            }) as r:
                res = await r.json()
                return base64ToBufferInputStream(res['plot_image'])

    @staticmethod
    async def remainsProduct(message) -> bytes:
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.get(f"{apiURL_ML}/v1/ml/analytics/leftover_info", params={
                "user_id": user.db_id,
            }) as r:
                res = await r.json()
                return base64ToBufferInputStream(res['plot_image'])


productAnalysisRouter = Router()


@productAnalysisRouter.message(ProductState.productWaitActions, F.text == ANALYZE_PRODUCT_BUTTON_TEXT,
                               flags={"rights": "analysis_product"})
@productAnalysisRouter.message(AppState.productAnalysis, F.text == ANALYZE_PRODUCT_BUTTON_TEXT,
                               flags={"rights": "analysis_product"})
async def productAnalysisInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.productAnalysis)
    print((await state.get_data())['productName'])
    await ProductAnalysisActions.pickProduct(message, (await state.get_data())['productName'])

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
    remainsProduct = await ProductAnalysisActions.remainsProduct(message)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(remainsProduct, filename="remains.png"))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == LAST_N_PURCHASE_BUTTON_TEXT)
async def lastNPurchase(message: Message, state: FSMContext) -> None:
    lastNPurchase = await ProductAnalysisActions.lastNPurchase(message, 5)

    await bot.send_document(message.chat.id,
                            document=BufferedInputFile(lastNPurchase, filename="last5.xlsx"))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == DEBIT_CREDIT_PRODUCT_BUTTON_TEXT)
async def debitCreditProduct(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=PRICE_BUTTON_TEXT),
        KeyboardButton(text=AMOUNT_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=DEBIT_CREDIT_PRODUCT_MESSAGE_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == PRICE_BUTTON_TEXT)
async def debit(message: Message, state: FSMContext) -> None:
    price = await ProductAnalysisActions.debitCredit(message, True)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(price, filename="price.png"))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == AMOUNT_BUTTON_TEXT)
async def credit(message: Message, state: FSMContext) -> None:
    amount = await ProductAnalysisActions.debitCredit(message, False)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(amount, filename="amount.png"))


@productAnalysisRouter.message(AppState.productAnalysis, F.text == STATISTIC_BUTTON_TEXT)
async def suggestProduct(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=YEAR_TEXT),
        KeyboardButton(text=QUARTER_TEXT),
        KeyboardButton(text=MONTH_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(ProductState.productStatistic)
    await message.answer(text=CHOSE_PERIOD_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productAnalysisRouter.message(ProductState.productStatistic, F.text == YEAR_TEXT)
@productAnalysisRouter.message(ProductState.productStatistic, F.text == QUARTER_TEXT)
@productAnalysisRouter.message(ProductState.productStatistic, F.text == MONTH_TEXT)
async def suggestProductYear(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.productStatisticChoosePeriod)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=AMOUNT_OF_PURCHASES_BUTTON_TEXT),
        KeyboardButton(text=PRICE_OF_PURCHASES_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    period: int = 0
    if message.text == YEAR_TEXT:
        period = 1
    elif message.text == QUARTER_TEXT:
        period = 2
    elif message.text == MONTH_TEXT:
        period = 3

    await state.update_data(productStatisticPeriod=period)

    await message.answer(text="Выберите сумму/количество",
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@productAnalysisRouter.message(ProductState.productStatisticChoosePeriod, F.text == AMOUNT_OF_PURCHASES_BUTTON_TEXT)
async def amountStatistic(message: Message, state: FSMContext) -> None:
    period: int = (await state.get_data())['productStatisticPeriod']
    statisticPurchaseAmount = await ProductAnalysisActions.statisticPurchase(message, period, False)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(statisticPurchaseAmount, filename="amount.png"))


@productAnalysisRouter.message(ProductState.productStatisticChoosePeriod, F.text == PRICE_OF_PURCHASES_BUTTON_TEXT)
async def priceStatistic(message: Message, state: FSMContext) -> None:
    period: int = (await state.get_data())['productStatisticPeriod']
    statisticPurchasePrice = await ProductAnalysisActions.statisticPurchase(message, period, True)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(statisticPurchasePrice, filename="amount.png"))
