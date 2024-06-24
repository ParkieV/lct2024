"""
Раздел <Создание закупки>
"""
import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import apiURL, AsyncSessionDB
from db.db import User
from db.db_utils import getUser
from handlers.choose_purchase import choosePurchaseActionList
from res.create_new_purchase_text import *
from res.general_actions_text import *
from state.app_state import AppState
from state.create_new_purchase_state import CreateNewPurchaseState


class CrateNewPurchaseActions:
    @staticmethod
    async def createPurchase(message, purchase_header):
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.post(f"{apiURL}/user/purchase/", json={
                "id": purchase_header['id'],
                "user_id": user.id,
                "lotEntityId": purchase_header['lotEntityId'],
                "customerId": purchase_header["CustomerId"]
            }) as r:
                print(await r.json(), r.status)


cretePurchaseRouter = Router()


@cretePurchaseRouter.message(AppState.generalActions, F.text == CREATE_PURCHASE_BUTTON_TEXT,
                             flags={"rights": "create_purchase"})
@cretePurchaseRouter.message(AppState.createPurchase, F.text == CREATE_PURCHASE_BUTTON_TEXT,
                             flags={"rights": "create_purchase"})
async def createNewPurchaseInit(message: Message, state: FSMContext) -> None:
    """
    Приветственное меню раздела <Создание закупки>
    """
    await state.set_state(AppState.createPurchase)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await state.set_state(CreateNewPurchaseState.id)
    await message.answer(text=CREATE_NEW_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))


@cretePurchaseRouter.message(CreateNewPurchaseState.id, F.text != BACK_BUTTON_TEXT)
async def enterId(message: Message, state: FSMContext) -> None:
    """
    Ввод идентификатор закупки
    """
    id: str = message.text
    await state.update_data(id=id)
    await state.set_state(CreateNewPurchaseState.lotId)


@cretePurchaseRouter.message(CreateNewPurchaseState.lotId, F.text != BACK_BUTTON_TEXT)
async def enterLotId(message: Message, state: FSMContext) -> None:
    """
    Ввод идентификатор лота
    """
    lotId: str = message.text
    await state.update_data(lotEntityId=lotId)
    await state.set_state(CreateNewPurchaseState.customerId)


@cretePurchaseRouter.message(CreateNewPurchaseState.customerId, F.text != BACK_BUTTON_TEXT)
async def enterCustomerId(message: Message, state: FSMContext) -> None:
    """
    Ввод идентификатор покупателя
    """
    customerId: str = message.text
    await state.update_data(CustomerId=customerId)
    await state.set_state(CreateNewPurchaseState.customerId)

    purchaseHeader: dict[str, str] = {
        "id": (await state.get_data())["id"],
        "lotEntityId": (await state.get_data())["lotEntityId"],
        "CustomerId": (await state.get_data())["CustomerId"],
    }
    await CrateNewPurchaseActions.createPurchase(message, purchaseHeader)

    async with AsyncSessionDB() as sessionDB:
        user: User = await sessionDB.get(User, message.chat.id)
        await user.createPurchase(purchaseHeader, sessionDB)

    await state.update_data(active_purchase=purchaseHeader['id'])
    await message.answer(text=CREATE_NEW_PURCHASE_SUCCESS_TEXT)
    await choosePurchaseActionList(message, state)
