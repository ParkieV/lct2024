"""
Раздел <Общие действия>
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from res.general_actions_text import *
from res.info_text import *
from state.app_state import AppState

generalActionsRouter = Router()


@generalActionsRouter.message(default_state, F.text == CONTINUE_BUTTON_TEXT)
@generalActionsRouter.message(AppState.info, F.text == CONTINUE_BUTTON_TEXT)
@generalActionsRouter.message(AppState.generalActions, F.text == CONTINUE_BUTTON_TEXT)
async def actionListHandlerInit(message: Message, state: FSMContext) -> None:
    await state.set_state(AppState.generalActions)

    keyboard = ReplyKeyboardBuilder().row(
        KeyboardButton(text=CHOOSE_PURCHASE_BUTTON_TEXT),
        KeyboardButton(text=CREATE_PURCHASE_BUTTON_TEXT),
    ).row(
        KeyboardButton(text=COMMON_ANALYSIS_BUTTON_TEXT),
        KeyboardButton(text=BALANCE_BUTTON_TEXT)
    ).row(
        KeyboardButton(text=BACK_BUTTON_TEXT)
    )

    await message.answer(text=ACTION_LIST_HELLO_TEXT, reply_markup=keyboard.as_markup(resize_keyboard=True))
