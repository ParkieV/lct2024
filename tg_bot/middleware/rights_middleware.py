import traceback
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject

from db.db import User
from db.db_utils import getUser
from res.general_text import PERMISSION_RIGHTS_ERROR_TEXT, SOMETHING_WRONG


class RightsCheckMiddleware(BaseMiddleware):
    """
    Middleware проверяет есть ли права у пользователя, если они требуются.
    """

    def __init__(self):
        pass

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Если пользователь не имеет прав, а они требуются, то отправляет пользователю сообщение с текстом
        {PERMISSION_RIGHTS_ERROR_TEXT}. Если пользователь имеет права, то вызывает функцию {handler}.
        """
        try:
            rights = get_flag(data, "rights")
            user: User = await getUser(event.chat.id)

            if rights is not None and user.type != 'admin':
                isValid: bool = True
                for right in rights:
                    if right not in user.rights:
                        isValid = False
                        break

                if not isValid:
                    raise PermissionError(PERMISSION_RIGHTS_ERROR_TEXT)

            return await handler(event, data)
        except PermissionError as pe:
            return await event.answer(PERMISSION_RIGHTS_ERROR_TEXT)
        except Exception as e:
            traceback.print_exception(e)
            return await event.answer(SOMETHING_WRONG)
