import base64

import aiohttp
from aiogram.types import Message

from config import apiURL_ML
from db.db import User
from db.db_utils import getUser


def base64ToBufferInputStream(img_base_64: str) -> bytes:
    """
    Функция преобразования base64 в байтовый поток
    :param img_base_64: base64 строка
    """
    imgBytes = img_base_64.encode(encoding='UTF-8')
    return base64.decodebytes(imgBytes)


class ApiActions(object):
    """Статический класс для работы с API"""

    @staticmethod
    async def speechToText(message: Message, voice_base64: str) -> str:
        """
        Функция получения текста из аудиозаписи

        :param message:
        :param voice_base64: аудиозапись в формате base64
        :return: расшифрованный текст
        """
        user: User = await getUser(message.chat.id)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{apiURL_ML}/v1/ml/s2t/transcribe", params={
                "user_id": user.db_id
            }, json={
                "audio": str(voice_base64)
            }) as r:
                if r.status == 200:
                    return (await r.json())['user_prompt']

                return ""
