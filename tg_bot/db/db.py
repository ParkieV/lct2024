import asyncio

from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.ext.asyncio import create_async_engine
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

    def __repr__(self):
        return f"<User(id={self.id}, isAuth={self.isAuth})>"


async def init_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_tables())
