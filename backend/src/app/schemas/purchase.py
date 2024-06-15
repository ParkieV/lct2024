from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel

from sqlalchemy.orm import Mapped


class PositionDTO(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    purchase_id: uuid.UUID
    DeliverySchedule__dates__end_date: datetime
    DeliverySchedule__dates__start_date: datetime
    DeliverySchedule__deliveryAmount: Decimal
    DeliverySchedule__deliveryConditions: str
    DeliverySchedule__year: int
    address__gar_id: str
    address__text: str
    entityId: str
    spgz_id: str
    nmc: Decimal
    okei_code: str
    purchaseAmount: Decimal
    spgzCharacteristics__characteristicName: str
    spgzCharacteristics__characteristicEnums__value: str
    spgzCharacteristics__conditionTypeId: str
    spgzCharacteristics__kpgzCharacteristicId: str
    spgzCharacteristics__okei_id: str
    spgzCharacteristics__selectType: str
    spgzCharacteristics__typeId: str
    spgzCharacteristics__value1: str
    spgzCharacteristics__value2: str

class PurchaseDTO(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    lotEntityId: str | None = None
    customerId: str | None = None
    positions: list[PositionDTO] | None

