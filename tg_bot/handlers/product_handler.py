"""
Раздел <Товар>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from pagination import Pagination
from res.action_list_text import ENTER_PRODUCT_NAME_BUTTON_TEXT
from res.product_text import *
from state.app_state import AppState
from state.product_state import ProductState

productRouter = Router()


@productRouter.message(default_state, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
@productRouter.message(AppState.actionList, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
@productRouter.message(AppState.product, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
async def productInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.productName)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=PRODUCT_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productRouter.message(ProductState.productName, F.text != BACK_BUTTON_TEXT)
async def enterProductName(message: Message, state: FSMContext) -> None:
    productName: str = message.text
    await state.update_data(productName=productName)
    print(productName)

    await state.set_state(ProductState.productNameSuggestedList)
    await showProductNameSuggestedList(message, state)


@productRouter.message(ProductState.productNameSuggestedList, F.text != BACK_BUTTON_TEXT)
async def showProductNameSuggestedList(message: Message, state: FSMContext) -> None:
    items = [
        "Пылесос синий",
        "Шторы рулонные",
        "Удлинитель 5 м",
        "Пилот на 5 гнезд",
        "Пилот на 6 гнезд",
        "Пилот на 7 гнезд",
        "Пилот на 8 гнезд",
        "Пилот на 9 гнезд",
        "Пилот на 10 гнезд",
        "Пилот на 11 гнезд",
        "Пилот на 12 гнезд",
        "Пилот на 13 гнезд",
        "Пилот на 14 гнезд",
        "Пилот на 15 гнезд",
        "Пилот на 16 гнезд",
        "Пилот на 17 гнезд",
        "Пилот на 18 гнезд",
    ]

    CALLBACK_DATA_PAGINATION_END = "product"
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
        await state.update_data(productName=pagination.items[index])
        print(pagination.items[index])

        await message.reply(text=pagination.items[index], reply_markup=ReplyKeyboardRemove())
        await state.set_state(ProductState.productActions)
        await productActionsInit(message, state)
    except Exception as e:
        print(e)
        await message.reply(text=INPUT_WRONG_INDEX)


@productRouter.message(ProductState.productActions)
async def productActionsInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductState.productWaitActions)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=ANALYZE_PRODUCT_BUTTON_TEXT),
        KeyboardButton(text=SUGGESTED_PRODUCT_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=PURCHASE_PRODUCT_BUTTON_TEXT),
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=PRODUCT_ACTIONS_TEXT((await state.get_data())["productName"]),
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@productRouter.message(ProductState.productWaitActions, F.text == SUGGESTED_PRODUCT_BUTTON_TEXT)
async def suggestProduct(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=YEAR_TEXT),
        KeyboardButton(text=QUARTER_TEXT),
        KeyboardButton(text=MONTH_TEXT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(ProductState.choosePeriod)
    await message.answer(text=CHOSE_PERIOD_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@productRouter.message(ProductState.choosePeriod, F.text == YEAR_TEXT)
@productRouter.message(ProductState.choosePeriod, F.text == QUARTER_TEXT)
@productRouter.message(ProductState.choosePeriod, F.text == MONTH_TEXT)
async def suggestProductYear(message: Message, state: FSMContext) -> None:
    period: str = message.text
    await message.answer(text=SELECT_PERIOD_TEXT(period))
    # with open('res/img/test.png', 'rb') as photo:
    #     result: Message = await bot.send_photo(message.chat.id,
    #                                            photo=BufferedInputFile(photo.read(), filename="test.png"),
    #                                            caption=SUGGESTED_PRODUCT_TEXT,
    #                                            # reply_markup=ReplyKeyboardRemove()
    #                                            )
