from abc import ABC, abstractmethod
from typing import Any, Type
import uuid
from pydantic import BaseModel

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

class AbstractDBRepository(ABC):
	_async_engine: AsyncEngine
	_engine: Engine

	@abstractmethod
	async def get_objects(self,
						*,
						expression: Any,
						out_schema: BaseModel,
						allow_none: bool = True,
						limit: int | None = None,
						offset: int | None = None) -> list[BaseModel] | None:
		pass

	@abstractmethod
	def get_object_by_id(self,
				id: uuid.UUID,
				*,
				expression: Any,
				out_schema: BaseModel,
				allow_none: bool = True) -> None | BaseModel:
		pass

	@abstractmethod
	def insert_object(self, item: BaseModel):
		pass

	@abstractmethod
	def delete_object_by_id(self, id: uuid.UUID):
		pass

	@abstractmethod
	def update_object_by_id(self, id: uuid.UUID, item: BaseModel):
		pass
