import asyncio

import aiohttp
import requests

# s = requests.Session()
#
# res = s.post('http://localhost:8000/api/auth/login/', json={
#     "email": "user@mos.ru",
#     "password": "test123"
# })


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/api/auth/login/", json={
            "email": "user@mos.ru",
            "password": "test123"
        }) as r:
            print(r.cookies.get('access_token'))


asyncio.run(main())
