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

	try:
		logger.debug("Start create user")
		user_repo = UserRepository(User)
		logger.debug("Start check user in DB")
		if await user_repo.get_object_by_email(body.email, session=session):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
								detail="User is existing")

		logger.debug("Start insert object")
		await user_repo.insert_object(body, out_schema=UserDTO, session=session)
	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")


	logger.debug("Start generate response")
	# Generate response
	response = Response(content="OK", media_type = "text/plain")
	response.status_code = 200

	return response

