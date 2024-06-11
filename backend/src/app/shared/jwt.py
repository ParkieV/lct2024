from typing import Annotated

import jwt
from fastapi import Header, Request

from app.schemas.token import TokenHeader, TokenPayload, AccessTokenPayload, RefreshTokenPayload
from app.shared.config import AUTH_SETTINGS
from app.shared.logger import logger


class JWT:
	"""
	This class allows you to perform various actions on access and refresh tokens. It uses PyJWT library for encoding and decoding tokens.
	"""
	_header: TokenHeader = TokenHeader(alg="HS256", typ="JWT")
	_CONFIG = AUTH_SETTINGS
	_secret_key = _CONFIG.secret_key
	_ISSUERS = ["http://localhost:8000", "http://127.0.0.1:8000"]

	@property
	def standard_header(self) -> TokenHeader:
		return self._header

	@standard_header.setter
	def payload(self, new_header: TokenHeader) -> None:
		self._header = new_header

	@classmethod
	def generate_token(cls, payload: TokenPayload, header: TokenHeader | None = None, **kwargs) -> str:
		if header:
			return jwt.encode(payload.model_dump(), cls._secret_key, header.alg, header.model_dump())
		else:
			return jwt.encode(payload.model_dump(), cls._secret_key, cls._header.alg, cls._header.model_dump())

	@classmethod
	def decode_token(cls, token: str) -> dict:
		"""
		Decode token.

		Args:
			token (str): token for decode.

		Raises:
			jwt.ExpiredSignatureError: Token is expired.
			jwt.InvalidTokenError: Invalid token.

		Returns:
			dict: Decoded token.
		"""
		# logger.debug(f"Time, when token are being decoded: {int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())}")

		try:
			return jwt.decode(token,
						   cls._secret_key,
						   algorithms=[cls._CONFIG.algorithm],
						   audience="https://localhost:8000/api",
						   issuer="https://localhost:8000/api")
		except jwt.ExpiredSignatureError as err:
			logger.error(f"Exception: {err.__class__.__name__}, details:{err}")
			raise jwt.InvalidTokenError("Token expired")
		except Exception as err:
			logger.error(f"Exception: {err.__class__.__name__}, details:{err}")
			raise jwt.InvalidTokenError("Invalid token")

	@classmethod
	async def check_access_token(cls, request: Request) -> None:
		"""
		Checks to see if token is valid.

		Args:
			token (str): token for validation.

		Raises:
			jwt.InvalidTokenError: Invalid token.

		Returns:
			None: Token is valid.
		"""
		if not (token := request.cookies.get("access_token")):
			raise ValueError("Access token not found")

		token_payload = AccessTokenPayload.model_validate(cls.decode_token(token))

		if token_payload.type != "access":
			raise jwt.InvalidTokenError("Invalid token")

		request.state.access_token = token
		request.state.token_payload = token_payload


	@classmethod
	async def check_refresh_token(cls, request: Request) -> None:
		"""
		Checks to see if token is valid.

		Args:
			token (str): token for validation.

		Raises:
			jwt.InvalidTokenError: Invalid token.

		Returns:
			None: Token is valid.
		"""
		if not (token := request.cookies.get("refresh_token")):
			raise ValueError("Refresh token not found")

		token_payload = RefreshTokenPayload.model_validate(cls.decode_token(token))

		if token_payload.type != "refresh":
			raise jwt.InvalidTokenError("Incorrect token type")

		request.state.refresh_token = token
		request.state.token_payload = token_payload

