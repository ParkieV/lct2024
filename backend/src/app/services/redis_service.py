from typing import Any
import redis
from app.services.db_service import AbstractDBService
from app.shared.config import REDIS_SETTINGS, RedisSettings


class RedisServiceFacade(AbstractDBService):
	_config: RedisSettings = REDIS_SETTINGS

	def __init__(self, config: RedisSettings | None = None) -> None:
		super().__init__(config)
		self._engine = redis.Redis(host=self._config.redis_host,
										port=self._config.redis_port,
										db=self._config.redis_database,
										password=self._config.redis_password,
										encoding='utf-8')

	def check_connection(self):
		if self._engine.ping():
			return True
		else:
			raise ConnectionError("Redis connection failed")

	def set_pair(self, key: str, value: str) -> None:

		self._engine.set(key, value)

	# For sets
	def add_members(self, key: str, *args) -> None:
		self._engine.sadd(key, *args)

	def get_values(self, key: str) -> list[Any] | None:
		if response := self._engine.smembers(key):
			return [item.decode('utf-8') for item in response] # type: ignore
		return None

	def get_keys(self) -> list[Any] | None:
		if keys := self._engine.keys(pattern="*"):
			return [item.decode('utf-8') for item in keys]  #type: ignore
		return None

	def check_key(self, key: str) -> bool:
		if (keys := self.get_keys()):
			if key not in keys:
				return False
			return True
		else:
			return False

	def delete_key(self, key: str) -> None:
		self._engine.delete(key)

	def delete_value(self, key: str, value: str) -> None:
		self._engine.srem(key, value)

	def check_value(self, key: str, value: str) -> bool:
		if self._engine.sismember(key, value): # Type: ignore
			return True
		return False
