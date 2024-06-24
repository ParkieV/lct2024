"""
Раздел с кнопками Назад для возврата на предыдущий шаг/этап
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from handlers.choose_purchase import choosePurchaseInit, choosePurchaseActionList
from handlers.create_product_purchase import purchaseProductInit
from handlers.general_actions import actionListHandlerInit
from handlers.general_purchases_analysis_handler import commonPurchaseAnalysisInit
from handlers.info_handler import infoHandlerInit
from handlers.product_actions import productActionsInit, predictProduct
from handlers.product_analysis_handler import productAnalysisInit, productStatistic
from handlers.product_handler import productInit
from res.general_purchases_analysis_text import TOP_EXPENSIVE_BUTTON_TEXT
from res.general_text import *
from state.app_state import AppState
from state.choose_purchase_state import ChoosePurchaseState
from state.create_new_purchase_state import CreateNewPurchaseState
from state.create_product_state import AddProductToPurchase
from state.general_purchase_analysis_state import CommonPurchaseAnalysisState
from state.info_state import InfoState
from state.product_state import ProductState

backRouter = Router()


@backRouter.message(default_state, F.text == BACK_BUTTON_TEXT)
@backRouter.message(InfoState.userInfo, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AppState.info, F.text == BACK_BUTTON_TEXT)
async def backActionUserInfo(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Информация о пользователе и помощь>.
    Используется по умолчанию, если есть только default_state
    """
    await state.set_state(AppState.info)
    await infoHandlerInit(message, state)


@backRouter.message(AppState.generalActions, F.text == BACK_BUTTON_TEXT)
async def backButtonActionList(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Список основных действий>
    """
    await infoHandlerInit(message, state)


@backRouter.message(AppState.commonPurchaseAnalysis, F.text == BACK_BUTTON_TEXT)
async def backButtonGeneralPurchaseAnalysis(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Общий анализ закупок>
    """
    await actionListHandlerInit(message, state)


@backRouter.message(AppState.balance, F.text == BACK_BUTTON_TEXT)
async def backButtonBalance(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Баланс>
    """
    await actionListHandlerInit(message, state)


@backRouter.message(ProductState.productName, F.text == BACK_BUTTON_TEXT)
async def backButtonProductName(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Товар>:`ввод имени товара`
    """
    await productInit(message, state)


@backRouter.message(ProductState.productNameSuggestedList, F.text == BACK_BUTTON_TEXT)
@backRouter.message(ProductState.enterProductNumFromList, F.text == BACK_BUTTON_TEXT)
async def backButtonProductSuggestedList(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Товар>:`выбор номер из списка товаров с пагинацией`
    """
    await productInit(message, state)


@backRouter.message(ProductState.productWaitActions, F.text == BACK_BUTTON_TEXT)
@backRouter.message(ProductState.productActions, F.text == BACK_BUTTON_TEXT)
async def backButtonProductActions(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Действия с товаром>
    """
    await productInit(message, state)


@backRouter.message(ProductState.predictChoosePeriod, F.text == BACK_BUTTON_TEXT)
async def backButtonProductPrediction(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Прогнозирование товара>
    """
    await productActionsInit(message, state)


@backRouter.message(ProductState.predictChooseType, F.text == BACK_BUTTON_TEXT)
async def backButtonProductPrediction(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Прогнозирование товара>:`Выбор типа прогнозирования`
    """
    await predictProduct(message, state)


@backRouter.message(ProductState.productStatistic, F.text == BACK_BUTTON_TEXT)
@backRouter.message(ProductState.productDebitCredit, F.text == BACK_BUTTON_TEXT)
@backRouter.message(ProductState.enterLastNProducts, F.text == BACK_BUTTON_TEXT)
async def backButtonProductAnalysis(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Аналитика по товару>
    """
    await productAnalysisInit(message, state)


@backRouter.message(ProductState.productStatisticChoosePeriod, F.text == BACK_BUTTON_TEXT)
async def backButtonProductAnalysis(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Статистика по товару>:`выбор типа статистики`
    """
    await productStatistic(message, state)


@backRouter.message(ProductState.waitPurchaseActions, F.text == BACK_BUTTON_TEXT)
async def backButtonPurchaseActions(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Закупка>
    """
    await productActionsInit(message, state)


@backRouter.message(AppState.activePurchase, F.text == BACK_BUTTON_TEXT)
@backRouter.message(ChoosePurchaseState.choosePurchase, F.text == BACK_BUTTON_TEXT)
async def backButtonActivePurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Выбор закупки>
    """
    await actionListHandlerInit(message, state)


@backRouter.message(ChoosePurchaseState.editPurchase, F.text == BACK_BUTTON_TEXT)
async def backButtonEditActivePurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Выбор закупки>:`редактировать закупку`
    """
    await state.set_state(AppState.generalActions)
    await choosePurchaseInit(message, state)


@backRouter.message(AppState.createPurchase, F.text == BACK_BUTTON_TEXT)
@backRouter.message(CreateNewPurchaseState.id, F.text == BACK_BUTTON_TEXT)
@backRouter.message(CreateNewPurchaseState.lotId, F.text == BACK_BUTTON_TEXT)
@backRouter.message(CreateNewPurchaseState.customerId, F.text == BACK_BUTTON_TEXT)
async def backButtonCreateNewPurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Создание новой закупки>:
    """
    await state.set_state(AppState.generalActions)
    await actionListHandlerInit(message, state)


@backRouter.message(AppState.createPurchase, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.initAdding, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.purchaseAmount, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.nmc, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.dateStart, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.dateEnd, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AddProductToPurchase.deliveryConditions, F.text == BACK_BUTTON_TEXT)
async def backButtonAddingProductToPurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Добавление товара в активную/текущую закупку>:`Изменение параметров товара`
    """
    await purchaseProductInit(message, state)


@backRouter.message(AddProductToPurchase.chooseAction, F.text == BACK_BUTTON_TEXT)
@backRouter.message(AppState.productAnalysis, F.text == BACK_BUTTON_TEXT)
async def backButtonAddingProductToPurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Добавление товара в активную/текущую закупку>:`Выбор действия`
    """
    await productActionsInit(message, state)


@backRouter.message(CommonPurchaseAnalysisState.choosePeriod, F.text == BACK_BUTTON_TEXT)
async def backButtonCommonPurchaseAnalysis(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Общий анализ закупок>
    """
    await commonPurchaseAnalysisInit(message, state)


@backRouter.message(ChoosePurchaseState.chooseActionsFromList, F.text == BACK_BUTTON_TEXT)
async def backButtonEditPurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Редактирование закупки>
    """
    await state.set_state(AppState.generalActions)
    await choosePurchaseInit(message, state)


@backRouter.message(ProductState.initActions, F.text == BACK_BUTTON_TEXT)
async def backButtonEditPurchase(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Товар>
    """
    await state.set_state(AppState.generalActions)
    await choosePurchaseActionList(message, state)


@backRouter.message(CommonPurchaseAnalysisState.chooseStatisticType, F.text == BACK_BUTTON_TEXT)
async def backButtonCommonAnalysisStatisticsByType(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Общий анализ>:`выбор типа графика`
    """
    await commonPurchaseAnalysisInit(message, state)


@backRouter.message(CommonPurchaseAnalysisState.enterN)
@backRouter.message(AppState.commonPurchaseAnalysis, F.text == TOP_EXPENSIVE_BUTTON_TEXT)
async def backButtonEnterNExpensivePurchases(message: Message, state: FSMContext) -> None:
    """
    Кнопка назад в блоке <Общий анализ>:`N самых дорогих закупок`:`Ввод N`
    """
    await state.set_state(AppState.generalActions)
    await commonPurchaseAnalysisInit(message, state)
