import os.path
from pydantic_settings import BaseSettings

from app.persistence.sqlalc_models import Base


class ServerSettings(BaseSettings):
	backend_host: str
	backend_port: int
	backend_allowed_methods: list[str]
	backend_cors_origins: list[str]
	backend_allowed_headers: list[str]
	backend_project_name: str
	backend_ml_uri: str

	@property
	def ml_uri(self) -> str:
		return self.backend_ml_uri


class AuthSettings(BaseSettings):
	secret_key: str
	algorithm: str
	access_expired_minutes: int
	refresh_expired_days: int


class PostgresSettings(BaseSettings):
	postgres_db: str
	postgres_user: str
	postgres_password: str
	db_host: str
	db_port: int | None = None

	@property
	def db_url(self) -> str:
		if self.db_port:
			return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}'
		else:
			return f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}/{self.postgres_db}'


class RedisSettings(BaseSettings):
	redis_host: str
	redis_port: int = 6379
	redis_password: str
	redis_database: int

SERVER_SETTINGS = ServerSettings(_env_file='.envs/app.env')  # type: ignore
AUTH_SETTINGS = AuthSettings(_env_file='.envs/auth.env')  # type: ignore
POSTGRES_SETTINGS = PostgresSettings(_env_file='.envs/db.env')  # type: ignore
REDIS_SETTINGS = RedisSettings(_env_file='.envs/redis.env')  # type: ignore
