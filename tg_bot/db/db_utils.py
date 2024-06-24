import traceback

import aiohttp

from config import apiURL, AsyncSessionDB
from db.db import User


async def logout(chat_id: int) -> bool:
    """
    Деаутентификация пользователя
    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: bool - успешный выход из аккаунта или нет
    """
    try:
        async with AsyncSessionDB() as sessionDB:
            user: User = await sessionDB.get(User, chat_id)
            async with aiohttp.ClientSession(cookies=user.cookies) as sessionApi:
                async with sessionApi.get(f'{apiURL}/auth/logout') as resp:
                    if resp.status != 200:
                        return False

            user.isAuth = False
            user.access_token = ''
            user.refresh_token = ''
            await sessionDB.commit()

        return True
    except Exception as e:
        traceback.print_exception(e)
        return False


async def getUser(chat_id: int) -> User:
    """
    Получение объекта пользователя из БД
    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: User - объект пользователя
    """
    async with AsyncSessionDB() as session:
        user: User = await session.get(User, chat_id)
        return user


async def getUserCookies(chat_id: int) -> dict[str, str]:
    """
    Получение cookies пользователя из БД
    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: dict[str, str] - cookies пользователя
    """
    return (await getUser(chat_id)).cookies
