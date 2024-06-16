import aiohttp

from tg_bot.config import apiURL, session
from tg_bot.db.db import User


async def logout(chat_id: int) -> bool:
    """

    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: bool - успешный выход из аккаунта или нет
    """
    try:
        user: User = await getUser(chat_id)

        async with aiohttp.ClientSession(cookies=user.cookies) as sessionApi:
            async with sessionApi.get(f'{apiURL}/api/auth/logout') as resp:
                if resp.status != 200:
                    return False

        await session.delete(user)
        await session.commit()

        return True
    except Exception as e:
        print(e)
        return False


async def getUser(chat_id: int) -> User:
    user: User = await session.get(User, chat_id)
    return user


async def getUserCookies(chat_id: int) -> dict[str, str]:
    return (await getUser(chat_id)).cookies
