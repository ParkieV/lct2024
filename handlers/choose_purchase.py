"""
Раздел <Выбор закупки>
"""
import io
import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import session
from db.db import User
from db.db_utils import getUser
from handlers.actions_list_handler import actionListHandlerInit
from pagination import Pagination
from res.action_list_text import CHOOSE_PURCHASE_BUTTON_TEXT
from res.choose_purchase_text import *
from res.general_text import BACK_BUTTON_TEXT, SOMETHING_WRONG
from state.app_state import AppState
from state.choose_purchase_state import ChoosePurchaseState

choosePurchaseRouter = Router()


@choosePurchaseRouter.message(AppState.activePurchase, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
@choosePurchaseRouter.message(AppState.actionList, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
@choosePurchaseRouter.message(ChoosePurchaseState.purchaseList, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
async def choosePurchaseInit(message: Message, state: FSMContext) -> None:
    user = await getUser(message.chat.id)
    items = [key for key, value in user.purchases.items()]

    if len(items) == 0:
        await message.answer(text=NO_PURCHASES_TEXT)
        await actionListHandlerInit(message, state)
        return

    await state.set_state(ChoosePurchaseState.purchaseList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )
    await message.answer(text=ACTIVE_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))

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
    await state.set_state(ChoosePurchaseState.chooseActionsFromList)
    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=EDIT_PURCHASE_BUTTON_TEXT),
        KeyboardButton(text=DOWNLOAD_PURCHASE_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=DELETE_PURCHASE_BUTTON_TEXT),
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    active_purchase: str = (await state.get_data())["active_purchase"]

    await message.answer(text=CHOOSE_PURCHASE_TEXT(active_purchase),
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@choosePurchaseRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == DOWNLOAD_PURCHASE_BUTTON_TEXT)
async def downloadActivePurchase(message: Message, state: FSMContext) -> None:
    user = await getUser(message.chat.id)

    purchases: dict = user.purchases[(await state.get_data())["active_purchase"]]
    bytes_data = json.dumps(purchases).encode('utf-8')

    with io.BytesIO(bytes_data) as jsonFile:
        await message.answer_document(BufferedInputFile(jsonFile.read(), filename=f"{purchases['id']}.json"))


@choosePurchaseRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == DELETE_PURCHASE_BUTTON_TEXT)
async def deleteActivePurchase(message: Message, state: FSMContext) -> None:
    user = await getUser(message.chat.id)
    user.deletePurchase((await state.get_data())["active_purchase"])
    await session.commit()

    await message.answer(text=DELETE_PURCHASE_SUCCESS_MESSAGE)
    await actionListHandlerInit(message, state)


# @choosePurchaseRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == EDIT_PURCHASE_BUTTON_TEXT)
# async def editPurchase(message: Message, state: FSMContext) -> None:
#     keyword = ReplyKeyboardBuilder().add(
#         KeyboardButton(text=BACK_BUTTON_TEXT),
#         KeyboardButton(text=DELETE_PURCHASE_BUTTON_TEXT),
#     ).row(
#         KeyboardButton(text=BACK_BUTTON_TEXT),
#     )
