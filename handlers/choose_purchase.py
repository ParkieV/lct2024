"""
Раздел <Выбор закупки>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import AsyncSessionDB, session
from db.db import User
from handlers.create_product_purchase import editPurchase
from pagination import Pagination
from res.action_list_text import ACTIVE_PURCHASE_BUTTON_TEXT, CHOOSE_PURCHASE_BUTTON_TEXT
from res.choose_purchase_text import *
from res.general_text import BACK_BUTTON_TEXT, SOMETHING_WRONG
from state.choose_purchase_state import ChoosePurchaseState
from state.app_state import AppState

choosePurchaseRouter = Router()


@choosePurchaseRouter.message(AppState.activePurchase, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
@choosePurchaseRouter.message(ChoosePurchaseState.purchaseList, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
async def choosePurchaseInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ChoosePurchaseState.purchaseList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=ACTIVE_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))

    user = await session.get(User, message.chat.id)

    print(user.purchases)

    items = []
    for key, value in user.purchases.items():
        items.append(key)

    pagination: Pagination = Pagination(
        items=items,
    )
    await state.update_data(pagination=pagination)
    await message.answer(**pagination.getMessageData())

    await state.set_state(ChoosePurchaseState.choosePurchase)


@choosePurchaseRouter.message(ChoosePurchaseState.choosePurchase, F.text != BACK_BUTTON_TEXT)
async def choosePurchaseFromList(message: Message, state: FSMContext) -> None:
    try:
        index: int = int(message.text) - 1
        pagination: Pagination = (await state.get_data())["pagination"]
        # TODO: вставить не просто текст, а объект с какими-то данными
        await state.update_data(active_purchase=pagination.items[index])

        await state.set_state(ChoosePurchaseState.actionsList)
        await choosePurchaseActionList(message, state)
    except Exception as e:
        print(e)
        await message.answer(text=SOMETHING_WRONG)


@choosePurchaseRouter.message(ChoosePurchaseState.actionsList, F.text != BACK_BUTTON_TEXT)
async def choosePurchaseActionList(message: Message, state: FSMContext) -> None:
    await state.set_state(ChoosePurchaseState.editPurchase)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=EDIT_PURCHASE_BUTTON_TEXT)
    ).add(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    active_purchase: str = (await state.get_data())["active_purchase"]

    await message.answer(text=CHOOSE_PURCHASE_TEXT(active_purchase),
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


# @choosePurchaseRouter.message(ChoosePurchaseState.editPurchase, F.text == EDIT_PURCHASE_BUTTON_TEXT)
# async def editActivePurchase(message: Message, state: FSMContext) -> None:
#     await state.update_data(edit_active_purchase_callback=choosePurchaseActionList)
#     await editPurchase(message, state, (await state.get_data())['active_purchase'])
