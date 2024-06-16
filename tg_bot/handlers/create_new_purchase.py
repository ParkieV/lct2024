"""
Раздел <Общий список действий>
"""
import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.config import session, apiURL
from tg_bot.db.db import User
from tg_bot.db.db_utils import getUser
from tg_bot.handlers.choose_purchase import choosePurchaseActionList
from tg_bot.res.action_list_text import *
from tg_bot.res.create_new_purchase_text import *
from tg_bot.state.app_state import AppState
from tg_bot.state.create_new_purchase_state import CreateNewPurchaseState


class CrateNewPurchaseActions:
    @staticmethod
    async def createNewPurchase(message, purchaseHeader):
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession(cookies=user.cookies) as session:
            async with session.post(f"{apiURL}/api/user/purchase/", json={
                "id": purchaseHeader['id'],
                "user_id": user.id,
                "lotEntityId": purchaseHeader['lotEntityId'],
                "customerId": purchaseHeader["CustomerId"]
            }) as r:
                print(await r.json(), r.status)


creteNewPurchaseRouter = Router()


@creteNewPurchaseRouter.message(AppState.actionList, F.text == CREATE_PURCHASE_BUTTON_TEXT,
                                flags={"rights": "create_purchase"})
@creteNewPurchaseRouter.message(AppState.createNewPurchase, F.text == CREATE_PURCHASE_BUTTON_TEXT,
                                flags={"rights": "create_purchase"})
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
    await CrateNewPurchaseActions.createNewPurchase(message, purchaseHeader)

    (await session.get(User, message.chat.id)).createPurchase(purchaseHeader)
    await session.commit()
    await session.close()

    await state.update_data(active_purchase=purchaseHeader['id'])
    await message.answer(text=CREATE_NEW_PURCHASE_SUCCESS_TEXT)
    await choosePurchaseActionList(message, state)
