from __future__ import annotations

from typing import Union

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Pagination(object):
    """
    Класс для генерации постраничного меню
    """

    CALLBACK_DATA_START_NEXT = "next_page_"
    CALLBACK_DATA_START_PREV = "prev_page_"

    def __init__(
            self,
            items: list,
            max_items_per_page: int = 5,
            callback_data_end: str = ""
    ):
        """
        :param items:
        :param max_items_per_page:
        :param callback_data_end: Строчка, которая будет конкатенирована в
        конце callback_data у inline-кнопок. То есть для кнопки `Вперед` и `Назад
        будет {self.CALLBACK_DATA_START_NEXT}{self.callback_data_end} и
        {self.CALLBACK_DATA_START_PREV}{self.callback_data_end} соответственно callback_data.
        По умолчанию будет callback_data_end - пустая строка.
        По умолчанию используются функции pagination.py:nextPageProduct и pagination.py:prevPageProduct
        """
        self.items: list = items
        self.__max_items_per_page: int = max_items_per_page
        self.__current_page: int = 0
        self.callback_data_end: str = callback_data_end
        self.keyboard: Union[InlineKeyboardMarkup] = self.__generateKeyboard()

        self.__start = self.__max_items_per_page * self.__current_page
        self.__end = self.__max_items_per_page * (self.__current_page + 1)

    def __recalcStartAndEnd(self) -> None:
        self.__start = self.__max_items_per_page * self.__current_page
        self.__end = self.__max_items_per_page * (self.__current_page + 1)

    def __generateKeyboard(self) -> Union[InlineKeyboardMarkup]:
        keyboardList = [
            InlineKeyboardButton(
                text="Назад",
                callback_data=f"{self.CALLBACK_DATA_START_PREV}{self.callback_data_end}"
            ) if self.__current_page != 0 else None,
            InlineKeyboardButton(
                text="Вперед",
                callback_data=f"{self.CALLBACK_DATA_START_NEXT}{self.callback_data_end}"
            ) if (self.__current_page + 1) * self.__max_items_per_page <= len(self.items) else None,
        ]

        keyboard = InlineKeyboardBuilder().row(
            *filter(lambda elem: elem is not None, keyboardList)
        )

        return keyboard.as_markup()

    def nextPage(self) -> Pagination:
        if (self.__current_page + 1) * self.__max_items_per_page <= len(self.items):
            self.__current_page += 1

        self.keyboard: Union[InlineKeyboardMarkup] = self.__generateKeyboard()
        self.__recalcStartAndEnd()
        return self

    def prevPage(self) -> Pagination:
        if self.__current_page != 0:
            self.__current_page -= 1

        self.keyboard: Union[InlineKeyboardMarkup] = self.__generateKeyboard()
        self.__recalcStartAndEnd()
        return self

    def __getMessageText(self) -> str:
        return "\n".join([
            f"{self.__current_page * self.__max_items_per_page + i + 1}. {item}" for i, item in
            enumerate(self.items[self.__start:self.__end])
        ])

    def getMessageData(self) -> dict[str, InlineKeyboardMarkup | str]:
        return {"text": self.__getMessageText(), "reply_markup": self.keyboard}


paginationRouter = Router()


@paginationRouter.callback_query(
    F.data == f"{Pagination.CALLBACK_DATA_START_NEXT}")
async def nextPageProduct(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая будет вызвана при нажатии на кнопку `Вперед`
    """
    pagination: Pagination = (await state.get_data())["pagination"]
    await callback.message.edit_text(**pagination
                                     .nextPage()
                                     .getMessageData())


@paginationRouter.callback_query(
    F.data == f"{Pagination.CALLBACK_DATA_START_PREV}")
async def prevPageProduct(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Функция, которая будет вызвана при нажатии на кнопку `Назад`
    """
    pagination: Pagination = (await state.get_data())["pagination"]
    await callback.message.edit_text(**pagination
                                     .prevPage()
                                     .getMessageData())
