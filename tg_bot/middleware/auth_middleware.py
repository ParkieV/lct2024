from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from db.db import User
from res.general_text import SOMETHING_WRONG
from res.login_text import *
from state.app_state import AppState


class AuthorizationCheckMiddleware(BaseMiddleware):
    """
    Middleware проверяет авторизован ли пользователь.
    """

    def __init__(self, session: Session, storage: MemoryStorage):
        self.session: Session = session
        self.storage: MemoryStorage = storage

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Если пользователь не авторизован, то отправляет пользователю сообщение с текстом {PERMISSION_AUTH_ERROR_TEXT}.
        Если пользователь авторизован, то вызывает функцию {handler}.
        :param handler:
        :param event:
        :param data:
        :return:
        """
        try:
            if await self.session.get(User, event.chat.id) is None:
                raise PermissionError(PERMISSION_AUTH_ERROR_TEXT)

            return await handler(event, data)
        except PermissionError as pe:
            await self.storage.set_state(AppState.login)

            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text=DO_AUTHORIZATION,
                callback_data=TRY_AGAIN_ACTION
            ))

            return await event.answer(pe.__str__(), reply_markup=builder.as_markup())
        except Exception as e:
            print(e)
            return await event.answer(SOMETHING_WRONG)
