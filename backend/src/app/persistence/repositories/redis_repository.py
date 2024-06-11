from typing import Any

from app.services.redis_service import RedisServiceFacade
from app.shared.logger import logger

class RedisRepository:
	_service = RedisServiceFacade()

	@classmethod
	def get_values_by_key(cls,
						  key: str,
						  *,
						  can_null: bool = True) -> list[Any] | None:
		result = cls._service.get_values(key)
		if can_null:
			return result
		else:
			if result:
				return result
			else:
				raise ValueError("Values not found")

	@classmethod
	def check_value_by_key(cls,
						   key: str,
						   value: str):
		return cls._service.check_value(key, value)

	@classmethod
	def insert_value_by_key(cls,
							key: str,
							value: Any):
		try:
			svalue = str(value)
		except Exception as err:
			raise ValueError("Can't encode to string")

		cls._service.add_members(key, svalue)

	@classmethod
	def insert_values_by_key(cls,
							key: str,
							value: list[Any]):
		try:
			svalue = str(value)
		except Exception as err:
			raise ValueError("Can't encode to string")

		if not cls._service.check_key(key):
			cls._service.set_pair(key, svalue)
		else:
			cls._service.add_members(key, *value)

	@classmethod
	def delete_value_by_key(cls,
							key: str,
							value: Any):
		if result := cls.get_values_by_key(key):
			logger.debug(f"num of results {len(result)}")
			if len(result) > 1:
				cls._service.delete_value(key, value)
			elif len(result) == 1:
				cls._service.delete_key(key)
		else:
			raise KeyError(f"Can't find values for key {key}")

