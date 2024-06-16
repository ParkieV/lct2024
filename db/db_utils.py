import aiohttp

from config import apiURL, session
from db.db import User


async def logout(chat_id: int) -> bool:
    """

    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: bool - успешный выход из аккаунта или нет
    """
    try:
        user: User = await session.get(User, chat_id)

        async with aiohttp.ClientSession(
                cookies={"access_token": user.access_token,
                         "refresh_token": user.refresh_token}) as sessionApi:
            async with sessionApi.get(f'{apiURL}/api/auth/logout') as resp:
                if resp.status != 200:
                    return False

        await session.delete(user)
        await session.commit()

        return True
    except Exception as e:
        print(e)
        return False
