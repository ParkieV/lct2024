import uuid
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, unique=True, primary_key=True, index=True)

user_right_association = Table(
    'user_right_association',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('right_id', UUID(as_uuid=True), ForeignKey('system_right.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    middle_name: Mapped[str] = mapped_column(String, default=None)
    last_name: Mapped[str] = mapped_column(String)
    telegram_nickname: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    work_org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('organization.id'), default=None)
    work_organization: Mapped["Organization"] = relationship('Organization', back_populates='employees')
    position_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('work_position.id'), default=None)
    position: Mapped["WorkPosition"] = relationship('WorkPosition')
    rights: Mapped[list["SystemRight"]] = relationship('SystemRight', secondary=user_right_association, back_populates='users')

class Organization(Base):
    __tablename__ = 'organization'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(String)
    employees: Mapped[list['User']] = relationship('User', back_populates='work_organization')
    positions: Mapped[list['WorkPosition']] = relationship('WorkPosition', back_populates='work_organization')

class WorkPosition(Base):
    __tablename__ = 'work_position'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(String)
    employees: Mapped[list['User']] = relationship('User', back_populates='position')
    work_org_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('organization.id'), default=None)
    work_organization: Mapped["Organization"] = relationship('Organization', back_populates='positions')

class SystemRight(Base):
    __tablename__ = "system_right"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name: Mapped[str] = mapped_column(String)
    users: Mapped[list['User']] = relationship('User', secondary=user_right_association, back_populates='rights')
