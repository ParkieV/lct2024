"""
Раздел <Общий список действий>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import AsyncSessionDB, session
from db.db import User
from handlers.choose_purchase import choosePurchaseActionList
from res.action_list_text import *
from res.create_new_purchase_text import *
from res.info_text import *
from state.app_state import AppState
from state.create_new_purchase_state import CreateNewPurchaseState

creteNewPurchaseRouter = Router()


@creteNewPurchaseRouter.message(AppState.actionList, F.text == CREATE_PURCHASE_BUTTON_TEXT)
@creteNewPurchaseRouter.message(AppState.createNewPurchase, F.text == CREATE_PURCHASE_BUTTON_TEXT)
async def createNewPurchaseInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.createNewPurchase)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(CreateNewPurchaseState.id)
    await message.answer(text=CREATE_NEW_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@creteNewPurchaseRouter.message(CreateNewPurchaseState.id, F.text != BACK_BUTTON_TEXT)
async def enterId(message: Message, state: FSMContext) -> None:
    id: str = message.text
    await state.update_data(id=id)
    await state.set_state(CreateNewPurchaseState.lotId)


@creteNewPurchaseRouter.message(CreateNewPurchaseState.lotId, F.text != BACK_BUTTON_TEXT)
async def enterLotId(message: Message, state: FSMContext) -> None:
    lotId: str = message.text
    await state.update_data(lotEntityId=lotId)
    await state.set_state(CreateNewPurchaseState.customerId)


@creteNewPurchaseRouter.message(CreateNewPurchaseState.customerId, F.text != BACK_BUTTON_TEXT)
async def enterLotId(message: Message, state: FSMContext) -> None:
    CustomerId: str = message.text
    await state.update_data(CustomerId=CustomerId)
    await state.set_state(CreateNewPurchaseState.customerId)

    purchaseHeader: dict[str, str] = {
        "id": (await state.get_data())["id"],
        "lotEntityId": (await state.get_data())["lotEntityId"],
        "CustomerId": (await state.get_data())["CustomerId"],
    }

    (await session.get(User, message.chat.id)).createPurchase(purchaseHeader)
    await session.commit()
    await session.close()

    await state.update_data(active_purchase=purchaseHeader['id'])
    await message.answer(text=CREATE_NEW_PURCHASE_SUCCESS_TEXT)
    await choosePurchaseActionList(message, state)
