"""
Раздел <Общий список действий>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from tg_bot.res.action_list_text import *
from tg_bot.res.info_text import *
from tg_bot.state.app_state import AppState

actionListRouter = Router()


@actionListRouter.message(default_state, F.text == CONTINUE_BUTTON_TEXT)
@actionListRouter.message(AppState.info, F.text == CONTINUE_BUTTON_TEXT)
@actionListRouter.message(AppState.actionList, F.text == CONTINUE_BUTTON_TEXT)
async def actionListHandlerInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.actionList)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=CHOOSE_PURCHASE_BUTTON_TEXT),
        KeyboardButton(text=CREATE_PURCHASE_BUTTON_TEXT),
        # KeyboardButton(text=ENTER_PRODUCT_NAME_BUTTON_TEXT),
        # KeyboardButton(text=ACTIVE_PURCHASE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=COMMON_ANALYSIS_BUTTON_TEXT),
        KeyboardButton(text=BALANCE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=ACTION_LIST_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))

# @actionListRouter.message(default_state, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
# @actionListRouter.message(AppState.actionList, F.text == ENTER_PRODUCT_NAME_BUTTON_TEXT)
# async def productGoTo(message: Message, state: FSMContext) -> None:
#     await productInit(message, state)


# @actionListRouter.message(AppState.actionList, F.text == CHOOSE_PURCHASE_BUTTON_TEXT)
# async def choosePurchaseGoTo(message: Message, state: FSMContext) -> None:
#     await choosePurchaseInit(message, state)
