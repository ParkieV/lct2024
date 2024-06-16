from aiogram.fsm.state import StatesGroup, State


# Название товара
# 1. "purchaseAmount": "Объем поставки"
# 2. "nmc": "Сумма спецификации"
# 3. Дата начала поставки:
# 4. Дата окончания поставки:
# 5. "deliveryConditions": "Условия поставки"
# 6. "entityId": "Сквозной идентификатор СПГЗ"
class AddProductToPurchase(StatesGroup):
    """
    Класс для описания состояний в разделе <Добавление товара в закупку>
    """

    purchaseAmount = State()
    nmc = State()
    dateStart = State()
    dateEnd = State()
    deliveryConditions = State()
    entityId = State()
