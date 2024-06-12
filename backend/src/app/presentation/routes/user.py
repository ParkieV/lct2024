import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status
import pytz
import uuid

from app.persistence.sqlalc_models import User
from app.schemas.user import CreateRequestBodyDTO, UserDTO
from app.persistence.repositories.pg_repository import UserRepository
from app.persistence.repositories.redis_repository import RedisRepository
from app.services.pg_service import PostgresServiceFacade
from app.schemas.token import AccessTokenPayload, RefreshTokenPayload
from app.shared.logger import logger
from app.shared.jwt import JWT
from app.shared.config import AUTH_SETTINGS

router = APIRouter(prefix="/user")

@router.post("/")
async def create_user(body: CreateRequestBodyDTO, session = Depends(PostgresServiceFacade.get_async_session)):

	logger.debug("Start create user")
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

