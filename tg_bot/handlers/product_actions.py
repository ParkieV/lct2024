"""
Раздел <Товар>
"""
import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import apiURL, bot, apiURL_ML
from db.db import User
from db.db_utils import getUserCookies, getUser
from res.product_text import *
from state.product_state import ProductState
from utils import base64ToBufferInputStream


class ProductActions:
    @staticmethod
    async def checkRegular(message, product_name: str) -> bool | None:
        async with aiohttp.ClientSession(cookies=await getUserCookies(message.chat.id)) as session:
            async with session.get(f"{apiURL}/search/regular", params={
                "user_pick": product_name
            }) as r:
                print(await r.text(), r.status)
                if r.status == 200:
                    res = await r.json()
                    return res['is_regular']

                return None

    @staticmethod
    async def predictProduct(message, period) -> bytes:
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{apiURL_ML}/v1/ml/forecast/forecast", params={
                "period": period,
                "user_id": user.db_id
            }) as r:
                res = await r.json()
                if res['state'] != 'Success':
                    return b''

                return base64ToBufferInputStream(res['plot_image'])


productActionsRouter = Router()


@productActionsRouter.message(ProductState.productActions)
async def productActionsInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.productWaitActions)

    stateData = await state.get_data()

    productName: str = stateData["product_name"]
    regularity: bool = await ProductActions.checkRegular(message, productName)

    keyboard = ReplyKeyboardBuilder()
    first_row = [KeyboardButton(text=ANALYZE_PRODUCT_BUTTON_TEXT),
                 KeyboardButton(text=SUGGESTED_PRODUCT_BUTTON_TEXT)] \
        if regularity else [KeyboardButton(text=ANALYZE_PRODUCT_BUTTON_TEXT)]

    keyboard.row(
        *first_row
    ).row(
        KeyboardButton(text=PURCHASE_PRODUCT_BUTTON_TEXT),
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.update_data(regularity=regularity)
    await message.answer(
        text=PRODUCT_ACTIONS_TEXT(productName, regularity),
        reply_markup=keyboard.as_markup(resize_keyboard=True))


@productActionsRouter.message(ProductState.productWaitActions, F.text == SUGGESTED_PRODUCT_BUTTON_TEXT,
                              flags={"rights": "permission_suggestion"})
async def predictProduct(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=YEAR_TEXT),
        KeyboardButton(text=QUARTER_TEXT),
        KeyboardButton(text=MONTH_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(ProductState.predictChoosePeriod)
    await message.answer(text=PREDICT_PRODUCT_PERIOD_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productActionsRouter.message(ProductState.predictChoosePeriod, F.text == YEAR_TEXT)
@productActionsRouter.message(ProductState.predictChoosePeriod, F.text == QUARTER_TEXT)
@productActionsRouter.message(ProductState.predictChoosePeriod, F.text == MONTH_TEXT)
async def predictProductByPeriod(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.predictChooseType)

    period: int = 1
    if message.text == YEAR_TEXT:
        period = 1
    elif message.text == QUARTER_TEXT:
        period = 2
    elif message.text == MONTH_TEXT:
        period = 3

    predictRes = await ProductActions.predictProduct(message, period)
    await bot.send_photo(message.chat.id,
                         photo=BufferedInputFile(predictRes, filename="predict.png"))

    # keyboard = ReplyKeyboardBuilder().row(
    #     KeyboardButton(text=AMOUNT_BUTTON_TEXT),
    #     KeyboardButton(text=PRICE_BUTTON_TEXT),
    # ).row(
    #     KeyboardButton(text=BACK_BUTTON_TEXT)
    # )
    #
    # await message.answer(text=SELECT_PERIOD_TEXT(message.text),
    #                      reply_markup=keyboard.as_markup(resize_keyboard=True))

# @productActionsRouter.message(ProductState.predictChooseType, F.text == PRICE_BUTTON_TEXT)
# async def predictProductByPrice(message: Message, state: FSMContext) -> None:
#     period: int = (await state.get_data())['period']
#     price = await ProductActions.predictProduct(message, period)
#
#     await bot.send_photo(message.chat.id,
#                          photo=BufferedInputFile(price, filename="price.png"))
#
#
# @productActionsRouter.message(ProductState.predictChooseType, F.text == AMOUNT_BUTTON_TEXT)
# async def predictProductByAmount(message: Message, state: FSMContext) -> None:
#     period: int = (await state.get_data())['period']
#     amount = await ProductActions.predictProduct(message, period)
#
#     await bot.send_photo(message.chat.id,
#                          photo=BufferedInputFile(amount, filename="amount.png"))
