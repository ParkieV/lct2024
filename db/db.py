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

    id = Column(Integer, primary_key=True)
    db_id = Column(String, nullable=False)
    isAuth = Column(Boolean, nullable=False, default=False)
    purchases = Column("purchases", MutableDict.as_mutable(JSON()), default={})

    access_token = Column(String, nullable=True, default="")
    refresh_token = Column(String, nullable=True, default="")

    rights = Column(String, default="")
    type = Column(String, default="")

    balance = Column(Integer, default=0)

    def getAllProducts(self, purchase_id: str) -> list[str]:
        return [row['entityId'] for row in self.purchases[purchase_id]['rows']]

    def getAllPurchasesWithPrices(self) -> list[list[str | int]]:
        purchasesList: list[list[str | int]] = []
        for purchaseName in self.purchases.keys():
            price: int = 0
            for row in self.purchases[purchaseName]['rows']:
                price += int(row['nmc'])
            purchasesList.append([purchaseName, price])

        return purchasesList

    def getProductInPurchase(self, purchase_id: str, product_id: str) -> dict[str, str] | None:
        for row in self.purchases[purchase_id]['rows']:
            if row['entityId'] == product_id:
                return row
        return None

    async def setBalance(self, balance: int, session: AsyncSession):
        self.balance = balance
        session.add(self)
        await session.commit()

    async def setCookies(self, cookies: SimpleCookie, session: AsyncSession):
        """"Установка cookies"""
        self.access_token = cookies.get('access_token').value
        self.refresh_token = cookies.get('refresh_token').value

        session.add(self)
        await session.commit()

    async def createPurchase(self, json: dict[str, str], session: AsyncSession):
        """Создание закупки"""

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
        """Удаление закупки"""
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

    def updatePurchase(self):
        pass

    def __repr__(self):
        return f"<User(id={self.id}, isAuth={self.isAuth})>"


async def init_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_tables())
