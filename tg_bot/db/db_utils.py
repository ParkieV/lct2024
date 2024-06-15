from config import AsyncSessionDB
from db.db import User


async def logout(chat_id: int) -> bool:
    """

    :param chat_id: - идентификатор чата для получения объекта пользователя из БД
    :return: bool - успешный выход из аккаунта или нет
    """
    try:
        session = AsyncSessionDB()
        await session.delete(await session.get(User, chat_id))
        await session.commit()
        await session.close()
        return True
    except Exception as e:
        print(e)
        return False
