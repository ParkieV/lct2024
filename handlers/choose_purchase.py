"""
Раздел <Выбор закупки>
"""
import io
import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import AsyncSessionDB
from db.db import fillProductExample, PRODUCT_JSON_EXAMPLE
from db.db_utils import getUser
from handlers.general_actions import actionListHandlerInit
from pagination import Pagination
from res.choose_purchase_text import *
from res.general_actions_text import CHOOSE_PURCHASE_BUTTON_TEXT
from res.general_text import BACK_BUTTON_TEXT, SOMETHING_WRONG
from state.app_state import AppState
from state.choose_purchase_state import ChoosePurchaseState

choosePurchaseRouter = Router()


@choosePurchaseRouter.message(AppState.activePurchase, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
@choosePurchaseRouter.message(AppState.generalActions, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
@choosePurchaseRouter.message(ChoosePurchaseState.choosePurchase, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
async def choosePurchaseInit(message: Message, state: FSMContext) -> None:
    """
    Приветственное меню раздела <Выбор закупки>
    """
    user = await getUser(message.chat.id)
    purchases_list = [key for key, value in user.purchases.items()]

    if len(purchases_list) == 0:
        await message.answer(text=NO_PURCHASES_TEXT)
        await actionListHandlerInit(message, state)
        return

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )
    await message.answer(text=ACTIVE_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))

    pagination: Pagination = Pagination(
        items=purchases_list,
    )
    await state.update_data(pagination=pagination)
    await message.answer(**pagination.getMessageData())

    await state.set_state(ChoosePurchaseState.choosePurchase)


@choosePurchaseRouter.message(ChoosePurchaseState.choosePurchase, F.text != BACK_BUTTON_TEXT)
async def choosePurchaseFromList(message: Message, state: FSMContext) -> None:
    """
    Выбор закупки из списка
    """
    try:
        index: int = int(message.text) - 1
        pagination: Pagination = (await state.get_data())["pagination"]

        await state.update_data(active_purchase=pagination.items[index])

        await state.set_state(ChoosePurchaseState.actionsList)
        await choosePurchaseActionList(message, state)
    except Exception as e:
        await message.answer(text=SOMETHING_WRONG)


@choosePurchaseRouter.message(ChoosePurchaseState.actionsList, F.text != BACK_BUTTON_TEXT)
async def choosePurchaseActionList(message: Message, state: FSMContext) -> None:
    """
    Список кнопок с действиями над закупкой
    """
    await state.set_state(ChoosePurchaseState.chooseActionsFromList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=PRODUCT_INT_PURCHASE_BUTTON_TEXT),
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
    """
    Скачивание закупки в файл JSON
    """
    user = await getUser(message.chat.id)

    purchases: dict = user.purchases[(await state.get_data())["active_purchase"]].copy()
    if len(purchases['rows']) == 0:
        purchases['rows'] = [PRODUCT_JSON_EXAMPLE]
    else:
        for i in range(len(purchases['rows'])):
            purchases['rows'][i] = fillProductExample(purchases['rows'][i])
    bytes_data = json.dumps(purchases, ensure_ascii=False).encode('utf-8')

    with io.BytesIO(bytes_data) as jsonFile:
        await message.answer_document(BufferedInputFile(jsonFile.read(), filename=f"{purchases['id']}.json"))


@choosePurchaseRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == DELETE_PURCHASE_BUTTON_TEXT)
async def deleteActivePurchase(message: Message, state: FSMContext) -> None:
    """
    Удаление закупки
    """
    user = await getUser(message.chat.id)
    async with AsyncSessionDB() as sessionDB:
        await user.deletePurchase((await state.get_data())["active_purchase"], sessionDB)

    await message.answer(text=DELETE_PURCHASE_SUCCESS_MESSAGE)
    await actionListHandlerInit(message, state)
