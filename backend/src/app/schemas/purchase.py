from datetime import datetime
from decimal import Decimal
import uuid
import dateutil.parser
from pydantic import BaseModel, ValidationError, model_validator

from app.shared.logger import logger



class PositionDTO(BaseModel):
	id: uuid.UUID = uuid.uuid4()
	purchase_id: uuid.UUID
	DeliverySchedule__dates__end_date: datetime | None = None
	DeliverySchedule__dates__start_date: datetime | None = None
	DeliverySchedule__deliveryAmount: Decimal | None = None
	DeliverySchedule__deliveryConditions: str | None = None
	DeliverySchedule__year: int | None = None
	address__gar_id: str | None = None
	address__text: str | None = None
	entityId: str | None = None
	spgz_id: str | None = None
	nmc: Decimal | None = None
	okei_code: str | None = None
	purchaseAmount: Decimal | None = None
	spgzCharacteristics__characteristicName: str | None = None
	spgzCharacteristics__characteristicEnums__value: str | None = None
	spgzCharacteristics__conditionTypeId: str | None = None
	spgzCharacteristics__kpgzCharacteristicId: str | None = None
	spgzCharacteristics__okei_id: str | None = None
	spgzCharacteristics__selectType: str | None = None
	spgzCharacteristics__typeId: str | None = None
	spgzCharacteristics__value1: str | None = None
	spgzCharacteristics__value2: str | None = None

	@model_validator(mode='before')
	@classmethod
	def validate_dates(cls, values):
		for field in ['DeliverySchedule__dates__end_date', 'DeliverySchedule__dates__start_date']:
			value = getattr(values, field, None)
			if isinstance(value, str):
				try:
					setattr(values, field, dateutil.parser.parse(value))
				except ValueError:
					raise ValidationError(f"Invalid date format: {value}")
		return values

class PurchaseDTO(BaseModel):
	id_pk: uuid.UUID = uuid.uuid4()
	id: str | None = None
	user_id: uuid.UUID
	lotEntityId: str | None = None
	customerId: str | None = None
	positions: list[PositionDTO] | None

class CreatePurchaseBodyDTO(BaseModel):
	id_pk: uuid.UUID = uuid.uuid4()
	id: str | None = None
	user_id: uuid.UUID
	lotEntityId: str | None = None
	customerId: str | None = None

class CreatePurchasePositionBodyDTO(PositionDTO):
	pass
