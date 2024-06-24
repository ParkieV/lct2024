import asyncio
from http.cookies import SimpleCookie

from sqlalchemy import Column, Integer, Boolean, JSON, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base

engine = create_async_engine("sqlite+aiosqlite:///db/tg.db")

Base = declarative_base()

PRODUCT_JSON_EXAMPLE = {
    "DeliverySchedule": {
        "dates": {
            "end_date": "",
            "start_date": ""
        },
        "deliveryAmount": "",
        "deliveryConditions": "",
        "year": ""
    },
    "address": {
        "gar_id": "",
        "text": ""
    },
    "entityId": "",
    "id": "",
    "nmc": "",
    "okei_code": "",
    "purchaseAmount": "",
    "spgzCharacteristics": [
        {
            "characteristicName": "",
            "characteristicSpgzEnums": [
                {
                    "value": ""
                }
            ],
            "conditionTypeId": "",
            "kpgzCharacteristicId": "",
            "okei_id": "",
            "selectType": "",
            "typeId": "",
            "value1": "",
            "value2": ""
        }
    ]
}


def fillProductExample(json_local: dict[str, str]):
    """
    Заполнение данных из User.purchase в формате JSON по шаблону {PRODUCT_JSON_EXAMPLE} для rows
    """
    jsonExample = PRODUCT_JSON_EXAMPLE.copy()
    jsonExample['purchaseAmount'] = json_local['purchaseAmount']
    jsonExample['DeliverySchedule']['dates'] = {
        "end_date": json_local['dateEnd'],
        "start_date": json_local['dateStart']
    }
    jsonExample['DeliverySchedule']['deliveryConditions'] = json_local['deliveryConditions']
    jsonExample['nmc'] = json_local['nmc']
    jsonExample['entityId'] = json_local['entityId']

    return jsonExample


class User(Base):
    """
    Класс-представление пользователя в виде ORM для хранения данных об авторизации и т.д.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # id пользователя в локальной базы данных
    db_id = Column(String, nullable=False)  # id пользователя в базе данных на сервере
    isAuth = Column(Boolean, nullable=False, default=False)  # Флаг авторизации. Если авторизован, то True
    purchases = Column("purchases", MutableDict.as_mutable(JSON()), default={})  # Список закупок в формате JSON

    access_token = Column(String, nullable=True, default="")
    refresh_token = Column(String, nullable=True, default="")

    rights = Column(String, default="")  # Список прав доступа в виде строки `right1;right2;...`
    type = Column(String, default="")  # Тип пользователя. Администратор - admin, Пользователь - user

    balance = Column(Integer, default=0)  # Баланс пользователя в локальной базе данных

    def getAllProducts(self, purchase_id: str) -> list[str]:
        """
        Получение списка всех наименований/id товаров в закупке
        :param purchase_id: id закупки
        :return: Список наименований/id товаров в закупке
        """
        return [row['entityId'] for row in self.purchases[purchase_id]['rows']]

    def getAllPurchasesWithPrices(self) -> list[list[str | int]]:
        """
        Получение списка всех закупок с ценами
        :return: Список закупок в формате [['id закупки', 'Сумма'], ['id закупки', 'Сумма'], ...]
        """
        purchasesList: list[list[str | int]] = []
        for purchaseName in self.purchases.keys():
            price: int = 0
            for row in self.purchases[purchaseName]['rows']:
                price += int(row['nmc'])
            purchasesList.append([purchaseName, price])

        return purchasesList

    def getProductInPurchase(self, purchase_id: str, product_id: str) -> dict[str, str] | None:
        """
        Получение товара в закупке
        :param purchase_id: id закупки
        :param product_id: id товара
        :return: Словарь с данными товара
        """
        for row in self.purchases[purchase_id]['rows']:
            if row['entityId'] == product_id:
                return row
        return None

    async def setBalance(self, balance: int, session: AsyncSession):
        """
        Установка баланса пользователя
        """
        self.balance = balance
        session.add(self)
        await session.commit()

    async def setCookies(self, cookies: SimpleCookie, session: AsyncSession):
        """"
        Установка cookies
        """
        self.access_token = cookies.get('access_token').value
        self.refresh_token = cookies.get('refresh_token').value

        session.add(self)
        await session.commit()

    async def createPurchase(self, json: dict[str, str], session: AsyncSession):
        """
        Создание закупки
        """

        self.purchases[json['id']] = {
            'id': json['id'],
            'lotEntityId': json['lotEntityId'],
            'CustomerId': json['CustomerId'],
            "rows": [
            ]
        }
        session.add(self)
        await session.commit()

    async def putProduct(self, json: dict[str, str], purchase_id: str, session: AsyncSession):
        """
        Добавление/изменение товара в закупке
        """
        purchase = self.purchases.get(purchase_id, {})
        rows = purchase.get('rows', [])

        for i, row in enumerate(rows):
            if row['entityId'] == json['entityId']:
                rows[i] = json
                break
        else:
            rows.append(json)

        purchase['rows'] = rows
        self.purchases[purchase_id] = purchase

        session.add(self)
        await session.commit()

    async def deletePurchase(self, id: str, session: AsyncSession):
        """
        Удаление закупки
        """
        if self.purchases is None or id not in self.purchases.keys():
            return
        purchase = self.purchases.copy()
        purchase.pop(id)
        self.purchases = purchase

        session.add(self)
        await session.commit()

    @property
    def cookies(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
        }


async def init_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_tables())
