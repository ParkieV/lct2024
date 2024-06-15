import asyncio

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, BufferedInputFile

from config import dp, bot, stateStorage, AsyncSessionDB
from db.db import User
from handlers.actions_list_handler import actionListRouter
from handlers.active_purchase import activePurchaseRouter
from handlers.back_handler import backRouter
from handlers.balance_handler import balanceRouter
from handlers.create_purchase import createPurchaseRouter
from handlers.general_purchases_analysis_handler import commonPurchasesAnalysisRouter
from handlers.info_handler import infoRouter
from handlers.login_handler import loginRouter, loginHandlerInit
from handlers.product_analysis_handler import productAnalysisRouter
from handlers.product_handler import productRouter
from middleware.auth_middleware import AuthorizationCheckMiddleware
from pagination import paginationRouter
from res.general_text import *
from state.app_state import AppState


@dp.message(Command(START_COMMAND))
async def startBot(message: Message, state: FSMContext) -> None:
    """
    Стартовая функция для запуска бота. Сразу переводит на шаг "Авторизация".
    :param message:
    :param state:
    :return: None
    """

    await state.set_state(AppState.login)

    session = AsyncSessionDB()
    if await session.get(User, message.chat.id) is None:
        with open('res/img/hello.jpg', 'rb') as photo:
            result: Message = await bot.send_photo(message.chat.id,
                                                   photo=BufferedInputFile(photo.read(), filename="test.png"),
                                                   caption=BOT_HELLO_MESSAGE,
                                                   reply_markup=ReplyKeyboardRemove()
                                                   )
    await session.close()
    await loginHandlerInit(message=message, state=state)


if __name__ == "__main__":
    routerListForAuthRequired = [
        infoRouter,
        actionListRouter,
        commonPurchasesAnalysisRouter,
        balanceRouter,
        productRouter,
        productAnalysisRouter,
        createPurchaseRouter,
        activePurchaseRouter,
        paginationRouter,
        backRouter,
    ]
    for router in routerListForAuthRequired:
        # Устанавливаем middleware для проверки авторизации к роутерам
        router.message.middleware(AuthorizationCheckMiddleware(
            session=AsyncSessionDB(),
            storage=stateStorage
        ))

    dp.include_routers(
        loginRouter,
        *routerListForAuthRequired
    )
    asyncio.run(dp.start_polling(bot))
