from fastapi import HTTPException, status
from sqlalchemy import text
from typing import Any, AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError

from app.persistence.repositories.sql_error_handler import sql_validation_error
from app.services.db_service import AbstractDBService
from app.shared.config import POSTGRES_SETTINGS, PostgresSettings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from app.shared.logger import logger


class PostgresServiceFacade(AbstractDBService):
	_config: PostgresSettings = POSTGRES_SETTINGS
	_engine: AsyncEngine = create_async_engine(_config.db_url)

	@property
	def db_engine(self) -> AsyncEngine:
		return super().db_engine()

	def __init__(self, config: PostgresSettings | None = None) -> None:
		super().__init__(config)
		self._engine: AsyncEngine = create_async_engine(self._config.db_url)

	@classmethod
	async def check_connection(cls):
		async with AsyncSession(cls._engine, expire_on_commit=False) as session:
			query = text("""SELECT 1;""")

			await session.execute(query)
			await session.commit()
		return True

	@classmethod
	async def get_async_session(cls) -> AsyncGenerator[AsyncSession, Any]:

		async with AsyncSession(cls._engine, expire_on_commit=False) as session:
			try:
				yield session
			except SQLAlchemyError as database_error:
				await session.rollback()
				raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
									detail=sql_validation_error(database_error))
			except HTTPException as err:
				logger.error(f"Excepted error: {err}")
				raise err
			except Exception as e:
				await session.rollback()
				logger.error(f"Error in session: {e}")
				raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
									detail="Internal Server Error")

