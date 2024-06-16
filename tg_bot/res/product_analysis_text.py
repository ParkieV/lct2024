HOW_MANY_ITEMS_LEFT_BUTTON_TEXT = 'Сколько осталось товара'
LAST_N_PURCHASE_BUTTON_TEXT = 'Последние N закупок'
DEBIT_CREDIT_PRODUCT_BUTTON_TEXT = 'Оборот дебет/кредит'
STATISTIC_BUTTON_TEXT = 'Статистика закупок'

PRODUCT_ANALYSIS_HELLO_TEXT = f"""Выберите действие, которое вы хотите выполнить:\n
- Кнопка <b>{HOW_MANY_ITEMS_LEFT_BUTTON_TEXT}</b> позволит узнать, сколько осталось товара.\n
- Кнопка <b>{LAST_N_PURCHASE_BUTTON_TEXT}</b> позволит посмотреть список из N самых дорогих закупок за последний 
месяц, квартал или год.\n
- Кнопка <b>{DEBIT_CREDIT_PRODUCT_BUTTON_TEXT}</b> позволит посмотреть оборот дебит/кредит.\n
- Кнопка <b>{STATISTIC_BUTTON_TEXT}</b> позволит посмотреть статистику закупок по месяцам, кварталам или годам.\n"""

HOW_MANY_ITEMS_LEFT_MESSAGE_TEXT = lambda product: f"""Осталось 12 единиц <b>{product}</b> на складе."""

PRICE_BUTTON_TEXT = 'Сумма'
AMOUNT_BUTTON_TEXT = 'Количество'
DEBIT_CREDIT_PRODUCT_MESSAGE_TEXT = f"""Оборот дебит/кредит\n"""

STATISTIC_MESSAGE_TEXT = lambda product: f"""Статистика закупок для <b>{product}</b>:\n"""
