"""
Раздел <Товар>
"""
import base64
import traceback

import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import apiURL, bot
from db.db_utils import getUserCookies, getUser
from handlers.product_actions import productActionsInit
from pagination import Pagination
from res.choose_purchase_text import PRODUCT_INT_PURCHASE_BUTTON_TEXT
from res.product_text import *
from state.choose_purchase_state import ChoosePurchaseState
from state.product_state import ProductState
from utils import ApiActions


class ProductActions:
    @staticmethod
    async def getSuggestedList(message, product_name):
        async with aiohttp.ClientSession(cookies=await getUserCookies(message.chat.id)) as session:
            async with session.get(f"{apiURL}/search/catalog", params={
                "prompt": product_name
            }) as r:
                return (await r.json())[product_name]

    @staticmethod
    async def pickProduct(message, product_name: str) -> None:
        async with aiohttp.ClientSession(cookies=await getUserCookies(message.chat.id), headers={
            'accept': 'application/json',
        }) as session:
            async with session.post(f"{apiURL}/search/set_user_pick", params={
                "user_pick": product_name
            }) as r:
                print(await r.json())


productRouter = Router()


@productRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == PRODUCT_INT_PURCHASE_BUTTON_TEXT)
async def productInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.initActions)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=CREATE_BUTTON_TEXT),
        KeyboardButton(text=EDIT_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=REGULAR_PRODUCTS_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=PRODUCT_ACTION_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productRouter.message(ProductState.initActions, F.text == EDIT_BUTTON_TEXT)
async def editExistedProduct(message: Message, state: FSMContext) -> None:
    user = await getUser(message.chat.id)
    productList = user.getAllProducts((await state.get_data())['active_purchase'])

    if len(productList) == 0:
        await message.answer(text=NO_PRODUCTS_IN_PURCHASE_TEXT)
        await productInit(message, state)
        return

    await showProductNameSuggestedList(message, state, items=productList)


@productRouter.message(ProductState.initActions, F.text == REGULAR_PRODUCTS_BUTTON_TEXT)
async def regularProductList(message: Message, state: FSMContext) -> None:
    await message.answer(text=REGULAR_PRODUCTS_LIST)


@productRouter.message(ProductState.initActions, F.text == CREATE_BUTTON_TEXT)
async def enterProductNameForShowList(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.productName)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=PRODUCT_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productRouter.message(ProductState.productName, F.text, F.text != BACK_BUTTON_TEXT)
async def enterProductName(message: Message, state: FSMContext, product_name: str = None) -> None:
    productName: str = message.text if product_name is None else product_name
    await state.update_data(productName=productName)

    await state.set_state(ProductState.productNameSuggestedList)
    await showProductNameSuggestedList(message, state,
                                       items=await ProductActions.getSuggestedList(message, productName))


@productRouter.message(ProductState.productName, F.content_type == "voice")
async def enterProductNameByAudio(message: Message, state: FSMContext) -> None:
    await message.reply(text=RECOGNITION_CAN_TAKE_LONG_TIME_TEXT)

    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    binaryIO = await bot.download_file(file_path)

    voiceBase64 = base64.b64encode(binaryIO.read()).decode()
    recognizedText = await ApiActions.speechToText(message, voiceBase64)

    if len(recognizedText) == 0:
        await message.answer(text=SPEECH_DOES_NOT_RECOGNIZED_TEXT)
        return

    await enterProductName(message, state, product_name=recognizedText)


@productRouter.message(ProductState.productNameSuggestedList, F.text != BACK_BUTTON_TEXT)
async def showProductNameSuggestedList(message: Message, state: FSMContext, items) -> None:
    pagination: Pagination = Pagination(
        items=items,
    )
    await state.update_data(pagination=pagination)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=INPUT_PRODUCT_INDEX, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await message.answer(**pagination.getMessageData())
    await state.set_state(ProductState.enterProductNumFromList)


@productRouter.message(ProductState.enterProductNumFromList, F.text != BACK_BUTTON_TEXT)
async def getProductFromList(message: Message, state: FSMContext) -> None:
    try:
        index = int(message.text) - 1
        pagination: Pagination = (await state.get_data())["pagination"]
        # await state.update_data(productName=pagination.items[index])
        await state.update_data(product_name=pagination.items[index])
        print(pagination.items[index])

        await ProductActions.pickProduct(message, pagination.items[index])

        await message.reply(text=YOU_CHOOSE_THAT_PRODUCT_TEXT(pagination.items[index]),
                            reply_markup=ReplyKeyboardRemove())
        await state.set_state(ProductState.productActions)

        await productActionsInit(message, state)
    except Exception as e:
        traceback.print_exception(e)
        await message.reply(text=INPUT_WRONG_INDEX)

# @productRouter.message(ProductState.productActions)
# async def productActionsInit(message: Message, state: FSMContext) -> None:
#     await state.set_state(ProductState.productWaitActions)
#
#     user: User = await getUser(message.chat.id)
#     keyboard = ReplyKeyboardBuilder().row(
#         KeyboardButton(text=ANALYZE_PRODUCT_BUTTON_TEXT),
#         KeyboardButton(text=SUGGESTED_PRODUCT_BUTTON_TEXT)
#     ).row(
#         KeyboardButton(text=PURCHASE_PRODUCT_BUTTON_TEXT),
#         KeyboardButton(text=BACK_BUTTON_TEXT)
#     )
#
#     productName: str = (await state.get_data())["productName"]
#     regularity: bool = await ProductActions.checkRegular(message, productName)
#     await state.update_data(regularity=regularity)
#     await message.answer(
#         text=PRODUCT_ACTIONS_TEXT(productName, regularity),
#         reply_markup=keyboard.as_markup(resize_keyboard=True))
#
#
# @productRouter.message(ProductState.productWaitActions, F.text == SUGGESTED_PRODUCT_BUTTON_TEXT,
#                        flags={"rights": "permission_suggestion"})
# async def suggestProduct(message: Message, state: FSMContext) -> None:
#     keyboard = ReplyKeyboardBuilder().row(
#         KeyboardButton(text=YEAR_TEXT),
#         KeyboardButton(text=QUARTER_TEXT),
#         KeyboardButton(text=MONTH_TEXT),
#     ).row(
#         KeyboardButton(text=BACK_BUTTON_TEXT)
#     )
#
#     await state.set_state(ProductState.choosePeriod)
#     await message.answer(text=CHOSE_PERIOD_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))
#
#
# @productRouter.message(ProductState.choosePeriod, F.text == YEAR_TEXT)
# @productRouter.message(ProductState.choosePeriod, F.text == QUARTER_TEXT)
# @productRouter.message(ProductState.choosePeriod, F.text == MONTH_TEXT)
# async def suggestProductYear(message: Message, state: FSMContext) -> None:
#     await message.answer(text=SELECT_PERIOD_TEXT(message.text))
#
#     period: int = 1
#     if message.text == YEAR_TEXT:
#         period = 1
#     elif message.text == QUARTER_TEXT:
#         period = 2
#     elif message.text == MONTH_TEXT:
#         period = 3
#
#     price = await ProductActions.suggestPrice(message, period, True)
#     amount = await ProductActions.suggestPrice(message, period, False)
#
#     await bot.send_photo(message.chat.id,
#                          photo=BufferedInputFile(price, filename="price.png"))
#     await bot.send_photo(message.chat.id,
#                          photo=BufferedInputFile(amount, filename="amount.png"))
