import datetime
import pytz
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jwt import InvalidTokenError

from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.repositories.pg_repository import UserRepository
from app.persistence.repositories.redis_repository import RedisRepository
from app.persistence.sqlalc_models import User
from app.schemas.auth import LoginRequestBodyDTO, SignupRequestBodyDTO
from app.schemas.token import AccessTokenPayload, RefreshTokenPayload
from app.schemas.user import UserDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.config import AUTH_SETTINGS
from app.shared.jwt import JWT
from app.shared.logger import logger


router = APIRouter(prefix="/auth")


@router.post("/signup",
			 summary="Sign up user in system")
async def signup(body: SignupRequestBodyDTO, session: AsyncSession = Depends(PostgresServiceFacade.get_async_session)):

	pg_repo = UserRepository(User)
	if pg_repo.get_object_by_email(body.email, session=session):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail="User is existing")
	# Generate tokens
	time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
	access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
												   user_id=body.user.id,
												   email=body.user.email,
												   name=body.user.first_name + " " + body.user.last_name,
												   password=body.password,
												   aud="https://localhost:8000/api",
												   exp=time_temp +
													   datetime.timedelta(
														   minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
												   iat=time_temp,
												   jti= uuid.uuid4(),
												   type="access"
												   ))

	refresh_token = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
													user_id=body.user.id,
													name=body.user.first_name + " " + body.user.last_name,
													aud="https://localhost:8000/api",
													exp=time_temp + AUTH_SETTINGS.refresh_expired_days * 24 * 3600,
													iat=time_temp,
													jti= uuid.uuid4(),
													type="refresh"
													))

	RedisRepository.insert_value_by_key(str(body.user.id), refresh_token)

	# Generate response
	response = Response()
	response.set_cookie(key="access_token",
						value=access_token, httponly=True)
	response.set_cookie(key="refresh_token",
						value=refresh_token, httponly=True)
	response.status_code = 200
	response.body = b"OK"

	return response

@router.post("/login",
			 dependencies=[Depends(JWT.check_access_token)],
			 summary="Log in user in system")
async def auth(body: LoginRequestBodyDTO, request: Request):
	payload: AccessTokenPayload
	if not (payload := request.state.token_payload):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't find token payload")

	logger.debug(body)
	if not body.email != payload.email or body.password != payload.password:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")

	time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
	logger.debug(f"Time, when token are being generated: {time_temp}. Expired time: {time_temp + datetime.timedelta(minutes=30).seconds}")

	user_repo = UserRepository(User)
	if user_info := await user_repo.get_object_by_id(payload.user_id, out_schema=UserDTO):
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=payload.user_id,
													   email=payload.email,
													   name=payload.name,
													   password=payload.password,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(
															   minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= uuid.uuid4(),
													   type="access"
													   ))

		refresh_token = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
														user_id=payload.user_id,
														name=payload.name,
														aud="https://localhost:8000/api",
														exp=time_temp + AUTH_SETTINGS.refresh_expired_days * 24 * 3600,
														iat=time_temp,
														jti= uuid.uuid4(),
														type="refresh"
														))

		RedisRepository.insert_value_by_key(str(user_info.id), refresh_token)

		# Generate response
		response: Response = Response(
			content=UserDTO(**user_info.model_dump()).model_dump_json(), media_type="application/json")
		response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=900)
		response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=2592000)
		response.status_code = 200
		response.body = b"OK"

		return response
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/refresh",
			 dependencies=[Depends(JWT.check_refresh_token)],
			 summary="Refresh tokens for user")
async def refresh(request: Request):
	if not (payload := request.state.token_payload):
		raise InvalidTokenError("Can't find token payload")
	if not (refresh_token := request.state.refresh_token):
		raise InvalidTokenError("Can't find refresh token")

	logger.debug(f"Life time refresh token: {int(payload.exp) - int(payload.iat)}")
	if int(payload.exp) - int(payload.iat) != AUTH_SETTINGS.refresh_expired_days * 24 * 3600:
		logger.error(f"Token has uncorrect life time")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")

	logger.debug(f"User id: {payload.user_id}, refresh_token: {refresh_token}")
	if not RedisRepository.check_value_by_key(payload.user_id, refresh_token):
		logger.error("Refresh token not found")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh token not found")

	logger.info(f"User {payload.user_id} logged out")
	RedisRepository.delete_value_by_key(payload.user_id, refresh_token)

	user_repo = UserRepository(User)
	if user_info := await user_repo.get_object_by_id(payload.user_id, out_schema=UserDTO):
		# Generate tokens
		time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=user_info.user_id,
													   email=user_info.email,
													   name=user_info.name,
													   password=user_info.password,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(
															   minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= uuid.uuid4(),
													   type="access"
													   ))

		refresh_token = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
														user_id=payload.user_id,
														name=payload.name,
														aud="https://localhost:8000/api",
														exp=time_temp + AUTH_SETTINGS.refresh_expired_days * 24 * 3600,
														iat=time_temp,
														jti= uuid.uuid4(),
														type="refresh"
														))

		RedisRepository.insert_value_by_key(payload.user_id, refresh_token)

		# Generate response
		response = Response()
		response.set_cookie(key="access_token",
							value=access_token, httponly=True)
		response.set_cookie(key="refresh_token",
							value=refresh_token, httponly=True)

		return response
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="User not found")



@router.get("/logout",
			dependencies=[Depends(JWT.check_access_token)],
			summary="Logout user from system")
async def logout(request: Request) -> None:
	if not (payload := request.state.token_payload):
		raise InvalidTokenError("Can't find token payload")
	if not (refresh_token := request.cookies.get("refresh_token")):
		raise InvalidTokenError("Can't find refresh token")

	logger.debug(f"Life time access token: {int(payload.exp) - int(payload.iat)}")
	if int(payload.exp) - int(payload.iat) != AUTH_SETTINGS.access_expired_minutes * 60:
		logger.error(f"Token has uncorrect life time")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")

	logger.debug(f"User id: {payload.user_id}, refresh_token: {refresh_token}")
	if not RedisRepository.check_value_by_key(payload.user_id, refresh_token):
		logger.error("Refresh token not found")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh token not found")

	logger.info(f"User {payload.user_id} logged out")
	RedisRepository.delete_value_by_key(payload.user_id, refresh_token)

