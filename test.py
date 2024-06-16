import asyncio

import aiohttp


# s = requests.Session()
#
# res = s.post('http://localhost:8000/api/auth/login/', json={
#     "email": "user@mos.ru",
#     "password": "test123"
# })


async def main():
    cookies = None
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8000/api/auth/login", json={
            "email": "user@mos.ru",
            "password": "test123"
        }) as r:
            cookies = r.cookies

    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/api/v1/ml/check_regular", params={
            "user_pick": "Охранные услуги"
        }) as r:
            print((await r.json()))


asyncio.run(main())
