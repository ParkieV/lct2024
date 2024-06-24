from res.general_text import BACK_BUTTON_TEXT

INFO_BALANCE_BUTTON_TEXT = "Информация о балансе"
EDIT_BALANCE_BUTTON_TEXT = "Редактировать баланс"

BALANCE_HELLO_TEXT = f"""💰 Баланс  
  
Выберите действие, которое вы хотите выполнить с балансом при помощи кнопок 🧾 <b>{INFO_BALANCE_BUTTON_TEXT}</b> 
и ✏️ <b>{EDIT_BALANCE_BUTTON_TEXT}</b>.
 
↩️ Чтобы вернуться, нажмите кнопку <b>{BACK_BUTTON_TEXT}</b>."""


def INFO_BALANCE_MESSAGE_TEXT(purchases_list: list[list[str | int]], balance: int):
    def getPurchaseInfo() -> str:
        text = ""
        for i, purchase in enumerate(purchases_list):
            text += f"{i + 1}. {purchase[0]} - {purchase[1]} руб.\n"
        return text

    def getAllPurchasePrice() -> int:
        return sum([purchase[1] for purchase in purchases_list])

    return f"""💰 Информация о балансе  

Сейчас на вашем балансе <b>{balance} руб</b>.

В настоящее время стоимость ваших закупки:
{getPurchaseInfo()}
Общая стоимость всех закупок <b>{getAllPurchasePrice()} руб</b>
  
↩️ Чтобы вернуться, нажмите кнопку <b>{BACK_BUTTON_TEXT}</b>."""


INPUT_BALANCE_SUM_MESSAGE_TEXT = f"""💰 Редактировать баланс 
 
Введите сумму рублей, которую необходимо зачислить на баланс. Только цифры. 
 
↩️ Чтобы вернуться, нажмите кнопку <b>{BACK_BUTTON_TEXT}</b>."""

SUCCESS_EDIT_BALANCE_TEXT = "Баланс успешно изменён"
