import base64

import aiohttp

from config import apiURL_ML
from db.db import User
from db.db_utils import getUser


def isFloat(element: any) -> bool:
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False


def base64ToBufferInputStream(img_base_64: str) -> bytes:
    imgBytes = img_base_64.encode(encoding='UTF-8')
    return base64.decodebytes(imgBytes)


class ApiActions(object):
    @staticmethod
    async def speechToText(message, voice_base64: str) -> str:
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
