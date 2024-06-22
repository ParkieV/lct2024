from abc import ABC, abstractmethod
from typing import Any
from pydantic_settings import BaseSettings

from app.shared.logger import logger


class AbstractDBService(ABC):
	_config: BaseSettings
	_engine: Any

	@property
	def db_engine(self) -> Any:
		return self._engine

	def __init__(self, config: BaseSettings | None = None) -> None:
		if config:
			logger.info(f"Config: {config}")
			self._config = config

	@abstractmethod
	async def check_connection():
		pass

	@classmethod
	async def close_engine(cls) -> None:
		await cls._engine.dispose()
