import asyncio
from http.cookies import SimpleCookie
from typing import Any

from sqlalchemy import Column, Integer, Boolean, JSON, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base

engine = create_async_engine("sqlite+aiosqlite:///db/tg.db")

Base = declarative_base()


class User(Base):
    """
    Класс-представление пользователя в виде ORM для хранения данных об авторизации и т.д.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    isAuth = Column(Boolean, nullable=False, default=False)
    purchases = Column("purchases", MutableDict.as_mutable(JSON), default={})

    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self.access_token = ""
        self.refresh_token = ""

    def createPurchase(self, json: dict[str, str]):
        self.purchases[json['id']] = {
            'id': json['id'],
            'lotEntityId': json['lotEntityId'],
            'CustomerId': json['CustomerId'],
            "rows": [
                {
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
            ]
        }

    def deletePurchase(self, id: str):
        if self.purchases is None or id not in self.purchases.keys():
            return
        self.purchases.pop(id)

    def setCookies(self, cookies: SimpleCookie):
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
