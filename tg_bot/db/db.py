import asyncio
from http.cookies import SimpleCookie
from typing import Any

from sqlalchemy import Column, Integer, Boolean, JSON, String
from sqlalchemy.ext.asyncio import create_async_engine
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
    purchases = Column("purchases", MutableDict.as_mutable(JSON), default={})

    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)

    rights = Column(String, default="")
    type = Column(String, default="")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self.access_token = ""
        self.refresh_token = ""
        self.json = {}

    def createPurchase(self, json: dict[str, str]):
        """Создание закупки"""

        self.purchases[json['id']] = {
            'id': json['id'],
            'lotEntityId': json['lotEntityId'],
            'CustomerId': json['CustomerId'],
            "rows": [
            ]
        }

    def putProduct(self, json: dict[str, str], purchaseId: str):
        for i, row in enumerate(self.purchases[purchaseId]['rows']):
            if row['entityId'] == json['entityId']:
                self.purchases[purchaseId]['rows'][i] = json
                return

        self.purchases[purchaseId]['rows'].append(json)
        print(json)
        print(self.purchases[purchaseId])

    def getAllProducts(self, purchaseId: str) -> list[str]:
        print(self.purchases[purchaseId])
        return [row['entityId'] for row in self.purchases[purchaseId]['rows']]

    def deletePurchase(self, id: str):
        """Удаление закупки"""
        if self.purchases is None or id not in self.purchases.keys():
            return
        self.purchases.pop(id)

    def setCookies(self, cookies: SimpleCookie):
        """"Установка cookies"""
        self.access_token = cookies.get('access_token').value
        self.refresh_token = cookies.get('refresh_token').value

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
