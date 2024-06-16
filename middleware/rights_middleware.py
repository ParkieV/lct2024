from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject
from sqlalchemy.orm import Session

from db.db import User
from db.db_utils import getUser
from res.general_text import PERMISSION_RIGHTS_ERROR_TEXT, SOMETHING_WRONG


class RightsCheckMiddleware(BaseMiddleware):
    def __init__(self, session: Session, storage: MemoryStorage):
        self.session: Session = session
        self.storage: MemoryStorage = storage

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        try:
            rights = get_flag(data, "rights")
            user: User = await getUser(event.chat.id)

            if rights is not None:
                isValid: bool = True
                for right in rights:
                    if right not in user.rights:
                        isValid = False
                        break

                if not isValid:
                    raise PermissionError(PERMISSION_RIGHTS_ERROR_TEXT)

            return await handler(event, data)
        except PermissionError as pe:
            print(pe)
            return await event.answer(PERMISSION_RIGHTS_ERROR_TEXT)
        except Exception as e:
            print(e)
            return await event.answer(SOMETHING_WRONG)
