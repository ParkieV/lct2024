from datetime import datetime
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

class Base(DeclarativeBase):
	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())


class User(Base):
	__tablename__ = 'users'

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
	email: Mapped[str] = mapped_column(String)
	password: Mapped[str] = mapped_column(String)
	first_name: Mapped[str] = mapped_column(String)
	middle_name: Mapped[str] = mapped_column(String, default=None)
	last_name: Mapped[str] = mapped_column(String)
	telegram_nickname: Mapped[str] = mapped_column(String)
	phone: Mapped[str] = mapped_column(String)
	work_org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('organization.id'), default=None)
	work_organization: Mapped["Organization"] = relationship('Organization', back_populates='employees')
	position: Mapped[str | None] = mapped_column(String, default=None)
	rights: Mapped[str] = mapped_column(String, default="")


class Organization(Base):
	__tablename__ = 'organization'

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
	name: Mapped[str] = mapped_column(String)
	employees: Mapped[list['User']] = relationship('User', back_populates='work_organization')


class Balance(Base):
	__tablename__ = "balance"

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
	name: Mapped[str] = mapped_column(String)
	amount: Mapped[Numeric] = mapped_column(Numeric(14, 2), default=0)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))


class Purchase(Base):
	__tablename__ = "purchase"

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
	lotEntityId: Mapped[str] = mapped_column(String)
	customerId: Mapped[str] = mapped_column(String)
	positions: Mapped[list['PurchasePosition']] = relationship('PurchasePosition')


class PurchasePosition(Base):
	__tablename__ = "purchase_position"

	id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
	purchase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('purchase.id'))
	DeliverySchedule__dates__end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	DeliverySchedule__dates__start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	DeliverySchedule__deliveryAmount: Mapped[Numeric] = mapped_column(Numeric(14, 2), default=0)
	DeliverySchedule__deliveryConditions: Mapped[str] = mapped_column(String)
	DeliverySchedule__year: Mapped[int] = mapped_column(Integer)
	address__gar_id: Mapped[str] = mapped_column(String)
	address__text: Mapped[str] = mapped_column(String)
	entityId: Mapped[str] = mapped_column(String)
	spgz_id: Mapped[str] = mapped_column(String)
	nmc: Mapped[Numeric] = mapped_column(Numeric(14, 2), default=0)
	okei_code: Mapped[str] = mapped_column(String)
	purchaseAmount: Mapped[Numeric] = mapped_column(Numeric(14, 2), default=0)
	spgzCharacteristics__characteristicName: Mapped[str] = mapped_column(String)
	spgzCharacteristics__characteristicEnums__value: Mapped[str] = mapped_column(String)
	spgzCharacteristics__conditionTypeId: Mapped[str] = mapped_column(String)
	spgzCharacteristics__kpgzCharacteristicId: Mapped[str] = mapped_column(String)
	spgzCharacteristics__okei_id: Mapped[str] = mapped_column(String)
	spgzCharacteristics__selectType: Mapped[str] = mapped_column(String)
	spgzCharacteristics__typeId: Mapped[str] = mapped_column(String)
	spgzCharacteristics__value1: Mapped[str] = mapped_column(String)
	spgzCharacteristics__value2: Mapped[str] = mapped_column(String)
