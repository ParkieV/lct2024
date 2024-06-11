from typing import Any, Type
import uuid

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.repositories.db_repository import AbstractDBRepository
from app.persistence.sqlalc_models import Base, User
from app.schemas.user import UserDTO
from app.shared.logger import logger


class AsyncPostgresRepository(AbstractDBRepository):
	__model: Type[Base]

	@property
	def db_model(self) -> Type[Base]:
		return self.__model

	@db_model.setter
	def db_model(self, model: Type[Base]) -> None:
		self.__model = model

	def __init__(self, model: Type[Base]) -> None:
		self.__model = model

	async def get_objects(self,
						*,
						expression: Any,
						out_schema: Type[BaseModel],
						allow_none: bool = True,
						joins: Any = None,
						limit: int | None = None,
						offset: int | None = None,
						session: AsyncSession) -> None | list[BaseModel]:

		query = select(self.db_model).where(expression)
		if joins:
			query = query.options(selectinload(joins))
		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)

		if not (result := (await session.execute(query)).scalars().all()):
			if allow_none:
				return None
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
								detail=f"{self.db_model.__name__} not found")

		return [out_schema.model_validate(obj) for obj in result]

	async def insert_object(self,
							data: BaseModel,
							*,
							out_schema: Type[BaseModel],
							session: AsyncSession) -> BaseModel | None:

		logger.debug("Inserting object")
		try:
			db_model = self.db_model(**data.model_dump())
			session.add(db_model)
			await session.commit()
			await session.refresh(db_model)
			return out_schema.model_validate(db_model, from_attributes=True)
		except Exception as err:
			logger.error("Error while select object from DB:", f"{err}")
			raise err

	async def delete_object_by_id(self,
							id: uuid.UUID,
							*,
							session: AsyncSession) -> None:
		query = delete(self.db_model).where(self.db_model.id == id)
		await session.execute(query)
		await session.commit()

	async def update_object_by_id(self,
								  id: uuid.UUID,
								  updated_object: BaseModel,
								  *,
								  out_schema: Type[BaseModel],
								  session: AsyncSession
								  ) -> None:
		query = (update(self.db_model)
			.where(self.db_model.id == id)
			.values(updated_object.model_dump(exclude_unset=True))
			.execution_options(synchronize_session="evaluate"))

		await session.execute(query)
		await session.commit()

class UserRepository(AsyncPostgresRepository):


	def __init__(self, user_model: Type[User] = User) -> None:
		super().__init__(user_model)
		self.db_model: Type[User]


	async def get_object_by_id(self,
						id: uuid.UUID,
						*,
						session: AsyncSession,
						out_schema: Type[BaseModel] = UserDTO,
						allow_none: bool = True,
						joins: Any = None) -> Any:

		logger.debug("Getting object")
		query = select(self.db_model).where(self.db_model.id == id)
		if joins:
			query = query.options(selectinload(joins))

		try:
			logger.debug("send query to db")
			if not (result := (await session.execute(query)).scalar_one_or_none()):
				if allow_none:
					return None
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
									detail=f"{self.db_model.__name__} not found")

			logger.debug("send result")
			return out_schema.model_validate(result, from_attributes=True)
		except Exception as err:
			logger.error("Error while select object from DB:", f"{err}")
			raise err

	async def get_object_by_email(self,
						email: EmailStr,
						*,
						session: AsyncSession,
						out_schema: Type[BaseModel] = UserDTO,
						allow_none: bool = True,
						joins: Any = None) -> Any:

		logger.debug("Getting object")
		query = select(self.db_model).where(self.db_model.email == email)
		if joins:
			query = query.options(selectinload(joins))

		try:
			if not (result := (await session.execute(query)).scalar_one_or_none()):
				print(result)
				if allow_none:
					return None
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
									detail=f"{self.db_model.__name__} not found")

			return out_schema.model_validate(result, from_attributes=True)
		except Exception as err:
			logger.error("Error while select object from DB:", f"{err}")
			raise err


