from typing import Literal
import uuid
import hashlib
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenHeader(BaseModel):
	alg: str = Field(description="Алгоритм шифрования", default="HS256")
	typ: str = Field(description="Тип токена", default="JWT")


class TokenPayload(BaseModel):
	iss: str = Field(description="Источник токена",
					 examples=["https://example.com"])
	name: str | None = Field(description="Имя подписчика(пользователя)", default=None, examples=["John Doe"])
	aud: str = Field(description="Аудитория", examples=[
					 "https://example.com/api"])
	exp: int = Field(description="Время истечения токена",
					 examples=[int(datetime.now().timestamp())])
	iat: int = Field(description="Время создания токена",
					 examples=[int(datetime.now().timestamp())])
	jti: str = Field(description="Идентификатор токена",
					 default=uuid.uuid4(), examples=['d9ef1c50-514a-4095-9e51-1c35da329ee0'])
	type: Literal["access", "refresh"] = Field(description="тип JWT токена", examples=["access", "refresh"])

	# @model_validator(mode='before')  # type: ignore
	# @classmethod
	# def _validate(cls, data: dict) -> dict[str, Any]:
	# 	if isinstance(data, dict):
	# 		# Check issuer field
	# 		if isinstance(data.get("iss"), str):
	# 			issuer: str = data.get("iss")  # type: ignore
	# 			assert (
	# 				re.match(r"^https?://([a-zA-Z0-9\-\_]{1,}.){1,}[a-zA-Z0-9\-\_]{1,}$", issuer)), 'Issuer must be a valid URL'
	# 		else:
	# 			raise ValueError('Issuer must be a valid URL')
	# 		# Check subject field
	# 		assert (isinstance(data.get("user_id"), int)), 'Subject must be an integer'
	# 		# Check email field
	# 		if isinstance(data.get("email"), str):
	# 			email: str = data.get("email")  # type: ignore
	# 			assert (re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+$",
	# 					email)), 'Email must be a valid email address'
	# 		else:
	# 			raise ValueError('Email must be a valid email address')
	# 		# Check audience field
	# 		if isinstance(data.get("aud"), str):
	# 			issuer: str = data.get("aud")  # type: ignore
	# 			assert (
	# 				re.match(r"^https?://([a-zA-Z0-9\-\_]{1,}.){1,}[a-zA-Z0-9\-\_]{1,}(/[a-zA-Z0-9\-\_]{1,})*$", issuer)), 'Issuer must be a valid URL'
	# 		else:
	# 			raise ValueError('Issuer must be a valid URL')
	# 		# Check 'expiration time' field
	# 		assert (isinstance(data.get("exp"), int)
	# 				), "'Expiration time' must be an integer"
	# 		# Check 'not before time' field
	# 		assert (isinstance(data.get("nbf"), int)
	# 				), "'Not before time' must be an integer"
	# 		exp: int = data.get("exp")  # type: ignore
	# 		nbf: int = data.get("nbf")  # type: ignore
	# 		assert (exp > nbf), "'Expiration time' must be after 'Not before time'"
	# 		# Check 'issued at' field
	# 		assert (isinstance(data.get("iat"), int)), "'Issued at' must be an integer"
	# 		iat: int = data.get("iat")  # type: ignore
	# 		assert (iat < exp), "'Expiration time' must be before 'Issued at'"
	# 		assert (iat <= nbf), "'Issued at' must be not after 'Not before time'"
	# 		# Check 'JWT ID' field
	# 		assert (isinstance(data.get("jti"), int)), "'JWT ID' must be an integer"

	# 		return data
	# 	else:
	# 		raise ValueError('Data must be a dictionary')

class AccessTokenPayload(TokenPayload):
	user_id: str = Field(description="Идентификатор пользователя", examples=["d9ef1c50-514a-4095-9e51-1c35da329ee0"])
	email: EmailStr = Field(description="Почта пользователя", examples=["example@example.com"])
	password: str = Field(description="Пароль пользователя")
	rights: str = Field(description="Права пользователя")

class RefreshTokenPayload(TokenPayload):
	user_id: str = Field(description="Идентификатор пользователя", examples=["d9ef1c50-514a-4095-9e51-1c35da329ee0"])
