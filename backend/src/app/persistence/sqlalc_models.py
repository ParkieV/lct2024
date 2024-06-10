import uuid
from sqlalchemy import UUID, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True, index=True)

class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    middle_name: Mapped[str] = mapped_column(String, default=None)
    last_name: Mapped[str] = mapped_column(String)
    telegram_nickname: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    work_org_id: Mapped[uuid.UUID] = mapped_column(UUID)
    work_organization: Mapped["Organization"] = relationship('organization', back_populates='employees')
    position_id: Mapped[uuid.UUID] = mapped_column(UUID)
    position: Mapped["WorkPosition"] = relationship('work_position')
    right_ids: Mapped[list[int]] = mapped_column(Integer)
    right: Mapped["SystemRight"] = relationship('system_right', back_populates='users')

class Organization(Base):
    __tablename__ = 'organization'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    employees: Mapped[list['User']] = relationship('user', back_populates='work_organization')
    positions: Mapped[list['WorkPosition']] = relationship('work_position', back_populates='work_organization')

class WorkPosition(Base):
    __tablename__ = 'work_organization'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    employees: Mapped[list['User']] = relationship('user', back_populates='position')
    work_org_id: Mapped[uuid.UUID] = mapped_column(UUID)
    work_organization: Mapped["Organization"] = relationship('organization', back_populates='positions')

class SystemRight(Base):
    __tablename__ = "system_right"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    users: Mapped[list['User']] = relationship('user', back_populates='right')
