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
async def signup(body: SignupRequestBodyDTO, session: AsyncSession = Depends(PostgresServiceFacade.get_async_session)) -> Response:

	logger.debug("Start signup")
	user_repo = UserRepository(User)
	logger.debug("Start check user in DB")
	if await user_repo.get_object_by_email(body.email, session=session):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
							detail="User is existing")

	logger.debug("Start insert object")
	await user_repo.insert_object(body, out_schema=UserDTO, session=session)

	try:
		logger.debug("Start generate tokens")
		# Generate tokens
		time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=str(body.id),
													   email=body.email,
													   name=body.first_name + " " + body.last_name,
													   password=body.password,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= str(uuid.uuid4()),
													   type="access"
													   ))

		refresh_token = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
														user_id=str(body.id),
														name=body.first_name + " " + body.last_name,
														aud="https://localhost:8000/api",
														exp=time_temp +
															int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()),
														iat=time_temp,
														jti= str(uuid.uuid4()),
														type="refresh"
														))

		logger.debug("Start insert into redis")
		RedisRepository.insert_value_by_key(str(body.id), refresh_token)
	except Exception as err:
		logger.error("Problem with tokens/Redis", {err})
		raise err

	logger.debug("Start generate response")
	# Generate response
	response = Response(content="OK", media_type = "text/plain")
	response.set_cookie(key="access_token",
						value=access_token, httponly=True, max_age=int(datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).total_seconds()))
	response.set_cookie(key="refresh_token",
						value=refresh_token, httponly=True, max_age=int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()))
	response.status_code = 200

	return response

@router.post("/login",
			 summary="Log in user in system",
			 response_model=UserDTO)
async def login(body: LoginRequestBodyDTO, request: Request, session: AsyncSession = Depends(PostgresServiceFacade.get_async_session)) -> Response:

	logger.debug(f"login request body: {body}")

	user_repo = UserRepository(User)
	if user_info := await user_repo.get_object_by_email(body.email, out_schema=UserDTO, session=session):
		if body.email != user_info.email or body.password != user_info.password:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")

		logger.debug("Generate token")
		time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=str(user_info.id),
													   email=user_info.email,
													   name=user_info.first_name + " " + user_info.last_name,
													   password=user_info.password,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= str(uuid.uuid4()),
													   type="access"
													   ))

		refresh_token = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
														user_id=str(user_info.id),
														name=user_info.first_name + " " + user_info.last_name,
														aud="https://localhost:8000/api",
														exp=time_temp + int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()),
														iat=time_temp,
														jti= str(uuid.uuid4()),
														type="refresh"
														))

		logger.debug("insert value to redis")
		RedisRepository.insert_value_by_key(str(user_info.id), refresh_token)

		# Generate response
		response: Response = Response(
			content=UserDTO(**user_info.model_dump()).model_dump_json(), media_type="application/json")
		response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=int(datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).total_seconds()))
		response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()))
		response.status_code = 200

		return response
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/refresh",
			 dependencies=[Depends(JWT.check_refresh_token)],
			 summary="Refresh tokens for user")
async def refresh(request: Request, session: AsyncSession = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise InvalidTokenError("Can't find token payload")
	if not (refresh_token := request.state.refresh_token):
		raise InvalidTokenError("Can't find refresh token")

	logger.debug(f"User id: {payload.user_id}, refresh_token: {refresh_token}")
	if not RedisRepository.check_value_by_key(payload.user_id, refresh_token):
		logger.error("Refresh token not found")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh token not found")

	logger.info(f"User {payload.user_id} deleted refresh token")
	RedisRepository.delete_value_by_key(payload.user_id, refresh_token)

	user_repo = UserRepository(User)
	if user_info := await user_repo.get_object_by_id(payload.user_id, out_schema=UserDTO, session=session):
		# Generate tokens
		time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=str(user_info.id),
													   email=user_info.email,
													   name=payload.name,
													   password=user_info.password,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= str(uuid.uuid4()),
													   type="access"
													   ))


		refresh_token_n = JWT.generate_token(RefreshTokenPayload(iss="https://localhost:8000/api",
														user_id=str(user_info.id),
														name=payload.name,
														aud="https://localhost:8000/api",
														exp=time_temp + int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()),
														iat=time_temp,
														jti= str(uuid.uuid4()),
														type="refresh"
														))

		logger.debug("insert value to redis")
		RedisRepository.insert_value_by_key(str(user_info.id), refresh_token_n)

		# Generate response
		response: Response = Response(content="OK", media_type="text/plain")
		response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=int(datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).total_seconds()))
		response.set_cookie(key="refresh_token", value=refresh_token_n, httponly=True, max_age=int(datetime.timedelta(days=AUTH_SETTINGS.refresh_expired_days).total_seconds()))
		response.status_code = 200

		return response

	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="User not found")



@router.get("/logout",
			dependencies=[Depends(JWT.check_access_token)],
			summary="Logout user from system")
async def logout(request: Request) -> Response:
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

	try:
		logger.info(f"User {payload.user_id} logged out")
		RedisRepository.delete_value_by_key(payload.user_id, refresh_token)

		response = Response(content="OK", media_type="text/plain")

		# Установка куки с истечением срока действия в прошлом
		past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
		response.set_cookie(key="access_token", value="", httponly=True, expires=past_time)
		response.set_cookie(key="refresh_token", value="", httponly=True, expires=past_time)

		return response
	except Exception as err:
		logger.error(f"Error occurated while deleting from Redis. Details: {err}")
		raise HTTPException(status_code=500, detail="Internal Server Error")
