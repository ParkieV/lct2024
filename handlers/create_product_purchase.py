"""
Раздел <Закупка>
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiohttp import ClientSession

from config import AsyncSessionDB, apiURL_ML
from db.db import User
from db.db_utils import getUser
from handlers.product_handler import productActionsInit
from res.product_text import *
from state.create_product_state import AddProductToPurchase
from state.product_state import ProductState

createPurchaseRouter = Router()


class CreateProductPurchaseActions(object):
    @staticmethod
    async def predictNextPurchaseValues(message: Message):
        user: User = await getUser(message.from_user.id)
        async with ClientSession() as session:
            async with session.get(f"{apiURL_ML}/v1/ml/forecast/forecast_next_purchase", params={
                "user_id": user.db_id
            }) as r:
                if r.status == 200:
                    return await r.json()

                return None


class CallbackDataAddingEnum(object):
    AMOUNT: str = "purchaseAmount"
    PRICE: str = "nmc"
    DATE_START: str = "dateStart"
    DATE_END: str = "dateEnd"
    DELIVERY_CONDITION: str = "deliveryConditions"


@createPurchaseRouter.message(ProductState.waitPurchaseActions, F.text == PURCHASE_PRODUCT_BUTTON_TEXT)
@createPurchaseRouter.message(ProductState.productWaitActions, F.text == PURCHASE_PRODUCT_BUTTON_TEXT)
async def purchaseProductInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AddProductToPurchase.chooseAction)

    stateData = await state.get_data()
    user: User = await getUser(message.from_user.id)
    purchase = stateData['active_purchase']
    product_name = stateData['product_name']
    purchaseProductData = user.getProductInPurchase(purchase, product_name)

    firstRow = [
        KeyboardButton(text=CREATE_PRODUCT_BUTTON_TEXT),
        KeyboardButton(text=EDIT_PRODUCT_BUTTON_TEXT)
    ] if purchaseProductData is not None else [KeyboardButton(text=CREATE_PRODUCT_BUTTON_TEXT)]

    keyboard = ReplyKeyboardBuilder().row(
        *firstRow
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT),
    )

    await message.answer(text=ADD_PRODUCT_TO_PURCHASE_MESSAGE_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@createPurchaseRouter.message(AddProductToPurchase.chooseAction, F.text == EDIT_PRODUCT_BUTTON_TEXT)
async def purchaseProductEdit(message: Message, state: FSMContext) -> None:
    stateData = await state.get_data()

    user: User = await getUser(message.from_user.id)
    purchase = stateData['active_purchase']
    product_name = stateData['product_name']

    purchaseProductData = user.getProductInPurchase(purchase, product_name)
    if purchaseProductData is None:
        await purchaseProductCreatingInit(message, state)
        return

    await purchaseProductCreatingInit(message, state, json=purchaseProductData)


@createPurchaseRouter.message(AddProductToPurchase.chooseAction, F.text == CREATE_PRODUCT_BUTTON_TEXT)
async def purchaseProductCreatingInit(message: Message, state: FSMContext, *, json: dict[str, str] = None) -> None:
    await state.set_state(AddProductToPurchase.initAdding)

    purchaseAmount = ""
    nmc = ""
    dateStart = ""
    dateEnd = ""
    deliveryConditions = ""

    if json is not None:
        purchaseAmount = json['purchaseAmount']
        nmc = json['nmc']
        dateStart = json['dateStart']
        dateEnd = json['dateEnd']
        deliveryConditions = json['deliveryConditions']
    else:
        regularity = (await state.get_data())['regularity']
        if regularity is not None and regularity:
            purchaseValues: dict = await CreateProductPurchaseActions.predictNextPurchaseValues(message)
            if purchaseValues is not None:
                purchaseAmount = purchaseValues['deliveryAmount']
                nmc = purchaseValues['nmc']
                dateStart = purchaseValues['start_date']
                dateEnd = purchaseValues['end_date']
                deliveryConditions = ""

    await state.update_data(purchaseAmount=purchaseAmount)
    await state.update_data(nmc=nmc)
    await state.update_data(dateStart=dateStart)
    await state.update_data(dateEnd=dateEnd)
    await state.update_data(deliveryConditions=deliveryConditions)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=FINISH_ADDING_PRODUCT),
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT),
    )
    await message.answer(text=ADD_PRODUCT_TO_PURCHASE_MESSAGE_TEXT,
                         reply_markup=keyboard.as_markup(resize_keyboard=True))

    inlineKeyboard = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text=ADD_PRODUCT_AMOUNT_BUTTON, callback_data=CallbackDataAddingEnum.AMOUNT),
    ).row(
        InlineKeyboardButton(text=ADD_PRODUCT_PRICE_BUTTON, callback_data=CallbackDataAddingEnum.PRICE),
    ).row(
        InlineKeyboardButton(text=ADD_PRODUCT_DATE_START_BUTTON, callback_data=CallbackDataAddingEnum.DATE_START),
    ).row(
        InlineKeyboardButton(text=ADD_PRODUCT_DATE_END_BUTTON, callback_data=CallbackDataAddingEnum.DATE_END),
    ).row(
        InlineKeyboardButton(text=ADD_PRODUCT_DELIVERY_BUTTON, callback_data=CallbackDataAddingEnum.DELIVERY_CONDITION),
    )

    await message.answer(text=CREATE_PURCHASE_INIT_MESSAGE_TEXT(purchaseAmount, nmc, dateStart, dateEnd),
                         reply_markup=inlineKeyboard.as_markup())


@createPurchaseRouter.callback_query(F.data.in_({
    CallbackDataAddingEnum.AMOUNT,
    CallbackDataAddingEnum.PRICE,
    CallbackDataAddingEnum.DATE_START,
    CallbackDataAddingEnum.DATE_END,
    CallbackDataAddingEnum.DELIVERY_CONDITION,
}))
async def purchaseProductClickInlineButton(callback: CallbackQuery, state: FSMContext, ) -> None:
    text: str = ""
    stateProduct: State | None = None

    match callback.data:
        case CallbackDataAddingEnum.AMOUNT:
            text = f"Введите <b>{ADD_PRODUCT_AMOUNT_BUTTON}</b>"
            stateProduct = AddProductToPurchase.purchaseAmount

        case CallbackDataAddingEnum.PRICE:
            text = f"Введите <b>{ADD_PRODUCT_PRICE_BUTTON}</b>"
            stateProduct = AddProductToPurchase.nmc

        case CallbackDataAddingEnum.DATE_START:
            text = f"Введите <b>{ADD_PRODUCT_DATE_START_BUTTON}</b>"
            stateProduct = AddProductToPurchase.dateStart

        case CallbackDataAddingEnum.DATE_END:
            text = f"Введите <b>{ADD_PRODUCT_DATE_END_BUTTON}</b>"
            stateProduct = AddProductToPurchase.dateEnd

        case CallbackDataAddingEnum.DELIVERY_CONDITION:
            text = f"Введите <b>{ADD_PRODUCT_DELIVERY_BUTTON}</b>"
            stateProduct = AddProductToPurchase.deliveryConditions

        case _:
            pass

    await state.set_state(stateProduct)
    await callback.message.answer(text=text)


@createPurchaseRouter.message(AddProductToPurchase.purchaseAmount,
                              (F.text != BACK_BUTTON_TEXT) & (F.text != FINISH_ADDING_PRODUCT))
async def purchaseAmount(message: Message, state: FSMContext) -> None:
    purchaseAmount = message.text
    await state.update_data(purchaseAmount=purchaseAmount)
    # await state.set_state(AddProductToPurchase.nmc)
    await message.answer(text=SETTING_VALUE)


@createPurchaseRouter.message(AddProductToPurchase.nmc,
                              (F.text != BACK_BUTTON_TEXT) & (F.text != FINISH_ADDING_PRODUCT))
async def nmc(message: Message, state: FSMContext) -> None:
    nmc = message.text
    await state.update_data(nmc=nmc)
    # await state.set_state(AddProductToPurchase.dateStart)
    await message.answer(text=SETTING_VALUE)


@createPurchaseRouter.message(AddProductToPurchase.dateStart,
                              (F.text != BACK_BUTTON_TEXT) & (F.text != FINISH_ADDING_PRODUCT))
async def dateStart(message: Message, state: FSMContext) -> None:
    dateStart = message.text
    await state.update_data(dateStart=dateStart)
    # await state.set_state(AddProductToPurchase.dateEnd)
    await message.answer(text=SETTING_VALUE)


@createPurchaseRouter.message(AddProductToPurchase.dateEnd,
                              (F.text != BACK_BUTTON_TEXT) & (F.text != FINISH_ADDING_PRODUCT))
async def dateEnd(message: Message, state: FSMContext) -> None:
    dateEnd = message.text
    await state.update_data(dateEnd=dateEnd)
    # await state.set_state(AddProductToPurchase.deliveryConditions)
    await message.answer(text=SETTING_VALUE)


@createPurchaseRouter.message(AddProductToPurchase.deliveryConditions,
                              (F.text != BACK_BUTTON_TEXT) & (F.text != FINISH_ADDING_PRODUCT))
async def deliveryConditions(message: Message, state: FSMContext) -> None:
    deliveryConditions = message.text
    await state.update_data(deliveryConditions=deliveryConditions)
    await message.answer(text=SETTING_VALUE)


@createPurchaseRouter.message(F.text == FINISH_ADDING_PRODUCT)
async def finishAddingProduct(message: Message, state: FSMContext) -> None:
    productData = {
        "purchaseAmount": (await state.get_data())['purchaseAmount'],
        "nmc": (await state.get_data())['nmc'],
        "dateStart": (await state.get_data())['dateStart'],
        "dateEnd": (await state.get_data())['dateEnd'],
        "deliveryConditions": (await state.get_data())['deliveryConditions'],
        "entityId": (await state.get_data())['product_name'],
    }
    purchaseId = (await state.get_data())['active_purchase']

    user: User = await getUser(message.chat.id)
    async with AsyncSessionDB() as session:
        await user.putProduct(productData, purchaseId, session)

    await message.answer(text=ADDING_SUCCESS)
    await productActionsInit(message, state)
