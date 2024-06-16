"""
Раздел <Активные закупки>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.create_purchase import editPurchase
from pagination import Pagination
from res.action_list_text import ACTIVE_PURCHASE_BUTTON_TEXT
from res.active_purchase_text import *
from res.general_text import BACK_BUTTON_TEXT, SOMETHING_WRONG
from state.active_purchase_state import ActivePurchaseState
from state.app_state import AppState

activePurchaseRouter = Router()


@activePurchaseRouter.message(AppState.activePurchase, F.text == ACTIVE_PURCHASE_BUTTON_TEXT)
@activePurchaseRouter.message(ActivePurchaseState.purchaseList, F.text == ACTIVE_PURCHASE_BUTTON_TEXT)
async def activePurchaseInit(message: Message, state: FSMContext) -> None:
    await state.set_state(ActivePurchaseState.purchaseList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=ACTIVE_PURCHASE_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))

    items = [
        "Закупка 1",
        "Закупка 2",
        "Закупка 3",
        "Закупка 4",
        "Закупка 5",
        "Закупка 6",
        "Закупка 7",
        "Закупка 8",
        "Закупка 9",
        "Закупка 10",
        "Закупка 11",
        "Закупка 12",
        "Закупка 13",
        "Закупка 14",
    ]

    pagination: Pagination = Pagination(
        items=items,
    )
    await state.update_data(pagination=pagination)
    await message.answer(**pagination.getMessageData())

    await state.set_state(ActivePurchaseState.choosePurchase)


@activePurchaseRouter.message(ActivePurchaseState.choosePurchase, F.text != BACK_BUTTON_TEXT)
async def chooseActivePurchase(message: Message, state: FSMContext) -> None:
    try:
        index: int = int(message.text) - 1
        pagination: Pagination = (await state.get_data())["pagination"]
        # TODO: вставить не просто текст, а объект с какими-то данными
        await state.update_data(active_purchase=pagination.items[index])

        await state.set_state(ActivePurchaseState.actionsList)
        await actionOnActivePurchase(message, state)
    except Exception as e:
        print(e)
        await message.answer(text=SOMETHING_WRONG)


@activePurchaseRouter.message(ActivePurchaseState.actionsList, F.text != BACK_BUTTON_TEXT)
async def actionOnActivePurchase(message: Message, state: FSMContext) -> None:
    await state.set_state(ActivePurchaseState.editPurchase)

    keyboard = ReplyKeyboardBuilder().add(
        KeyboardButton(text=EDIT_PURCHASE_BUTTON_TEXT)
    ).add(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    active_purchase: str = (await state.get_data())["active_purchase"]

    await message.answer(text=CHOOSE_PURCHASE_TEXT(active_purchase),
                         reply_markup=keyboard.as_markup(resize_keyboard=True))


@activePurchaseRouter.message(ActivePurchaseState.editPurchase, F.text == EDIT_PURCHASE_BUTTON_TEXT)
async def editActivePurchase(message: Message, state: FSMContext) -> None:
    await state.update_data(edit_active_purchase_callback=actionOnActivePurchase)
    await editPurchase(message, state, (await state.get_data())['active_purchase'])
