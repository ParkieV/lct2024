"""
Раздел <Закупка>
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.config import session
from tg_bot.db.db import User
from tg_bot.db.db_utils import getUser
from tg_bot.handlers.product_handler import productActionsInit
from tg_bot.res.product_text import *
from tg_bot.state.create_product_state import AddProductToPurchase
from tg_bot.state.product_state import ProductState

createPurchaseRouter = Router()


@createPurchaseRouter.message(ProductState.waitPurchaseActions, F.text == PURCHASE_PRODUCT_BUTTON_TEXT)
@createPurchaseRouter.message(ProductState.productWaitActions, F.text == PURCHASE_PRODUCT_BUTTON_TEXT)
async def purchaseProductInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AddProductToPurchase.purchaseAmount)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT),
    )

    await message.answer(text=CREATE_PURCHASE_INIT_MESSAGE_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@createPurchaseRouter.message(AddProductToPurchase.purchaseAmount, F.text != BACK_BUTTON_TEXT)
async def purchaseAmount(message: Message, state: FSMContext) -> None:
    purchaseAmount = message.text
    await state.update_data(purchaseAmount=purchaseAmount)
    await state.set_state(AddProductToPurchase.nmc)


@createPurchaseRouter.message(AddProductToPurchase.nmc, F.text != BACK_BUTTON_TEXT)
async def nmc(message: Message, state: FSMContext) -> None:
    nmc = message.text
    await state.update_data(nmc=nmc)
    await state.set_state(AddProductToPurchase.dateStart)


@createPurchaseRouter.message(AddProductToPurchase.dateStart, F.text != BACK_BUTTON_TEXT)
async def dateStart(message: Message, state: FSMContext) -> None:
    dateStart = message.text
    await state.update_data(dateStart=dateStart)
    await state.set_state(AddProductToPurchase.dateEnd)


@createPurchaseRouter.message(AddProductToPurchase.dateEnd, F.text != BACK_BUTTON_TEXT)
async def dateEnd(message: Message, state: FSMContext) -> None:
    dateEnd = message.text
    await state.update_data(dateEnd=dateEnd)
    await state.set_state(AddProductToPurchase.deliveryConditions)


@createPurchaseRouter.message(AddProductToPurchase.deliveryConditions, F.text != BACK_BUTTON_TEXT)
async def deliveryConditions(message: Message, state: FSMContext) -> None:
    deliveryConditions = message.text
    await state.update_data(deliveryConditions=deliveryConditions)

    productData = {
        "purchaseAmount": (await state.get_data())['purchaseAmount'],
        "nmc": (await state.get_data())['nmc'],
        "dateStart": (await state.get_data())['dateStart'],
        "dateEnd": (await state.get_data())['dateEnd'],
        "deliveryConditions": (await state.get_data())['deliveryConditions'],
        "entityId": (await state.get_data())['productName'],
    }

    user: User = await getUser(message.chat.id)
    user.putProduct(productData, (await state.get_data())['active_purchase'])
    await session.commit()

    await message.answer(text=ADDING_SUCCESS)
    await productActionsInit(message, state)
