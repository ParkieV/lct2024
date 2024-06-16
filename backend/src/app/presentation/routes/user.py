import datetime
import uuid
from app.persistence.repositories.redis_repository import RedisRepository
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import pytz

from app.persistence.sqlalc_models import User
from app.persistence.repositories.pg_repository import UserRepository
from app.presentation.routes.balance import router as balance_router
from app.presentation.routes.purchase import router as purchase_router
from app.schemas.user import CreateRequestBodyDTO, UpdateRequestBodyDTO, UserDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.jwt import JWT
from app.shared.logger import logger
from app.shared.config import AUTH_SETTINGS
from app.schemas.token import AccessTokenPayload

router = APIRouter(prefix="/user")

router.include_router(balance_router, tags=["User balances"])
router.include_router(purchase_router, tags=["User purchases"])


@router.post("/",
			 dependencies=[Depends(JWT.check_access_token)],
			 tags=["User CRUD"])
async def create_user(body: CreateRequestBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	if "add_user" not in payload.rights and payload.user_id == body.id:
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Start create user")
		user_repo = UserRepository(User)
		logger.debug("Start check user in DB")
		if await user_repo.get_object_by_email(body.email, session=db_session):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
								detail="User is existing")

		logger.debug("Start insert object")
		await user_repo.insert_object(body, out_schema=UserDTO, session=db_session)
	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")


	logger.debug("Start generate response")
	# Generate response
	response = Response(content="OK", media_type = "text/plain")
	response.status_code = 200

	return response

@router.patch("/",
			 dependencies=[Depends(JWT.check_access_token)],
			 tags=["User CRUD"])
async def update_user(body: UpdateRequestBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)) -> Response:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	print(payload.user_id != str(body.id))
	if "add_user" not in payload.rights and payload.user_id != str(body.id):
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Start update user")
		user_repo = UserRepository(User)

		logger.debug("Start update object")
		if body.email:
			payload.email = body.email
		if body.password:
			payload.password = body.password
		if body.first_name:
			payload.name = body.first_name + " " + payload.name.split(" ")[1]
		if body.last_name:
			payload.name = payload.name.split(" ")[0] + " " + body.last_name
		if body.rights:
			payload.rights = body.rights

		await user_repo.update_object_by_id(payload.user_id, body, session=db_session)


		time_temp: int = int(datetime.datetime.now(pytz.timezone('Europe/Moscow')).timestamp())
		access_token = JWT.generate_token(AccessTokenPayload(iss="https://localhost:8000/api",
													   user_id=str(payload.user_id),
													   email=payload.email,
													   name=payload.name,
													   password=payload.password,
													   rights=payload.rights,
													   aud="https://localhost:8000/api",
													   exp=time_temp +
														   datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).seconds,
													   iat=time_temp,
													   jti= str(uuid.uuid4()),
													   type="access"
													   ))

		response = Response(status_code=200, content="OK", media_type="text/plain")
		response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=int(datetime.timedelta(minutes=AUTH_SETTINGS.access_expired_minutes).total_seconds()))

		return response

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")

@router.delete("/",
			 dependencies=[Depends(JWT.check_access_token)],
			 tags=["User CRUD"])
async def delete_user(user_id: uuid.UUID, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)) -> Response:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	print(payload.user_id != str(user_id))
	if "add_user" not in payload.rights or payload.user_id == str(user_id):
		raise HTTPException(403, "Action is unavailable")

	try:
		user_repo = UserRepository(User)
		if not await user_repo.get_object_by_id(user_id, out_schema=UserDTO, session=db_session):
			raise HTTPException(404, "User not found")
		try:
			RedisRepository.delete_key(str(user_id))
		except:
			pass
		finally:
			await user_repo.delete_object_by_id(user_id, session=db_session)
			return Response(status_code=200, content="OK", media_type="text/plain")

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")


@router.get("/users",
			 dependencies=[Depends(JWT.check_access_token)],
			 tags=["User CRUD"],
			 summary="Get info about all users")
async def get_users(*, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	if "add_user" not in payload.rights:
		raise HTTPException(403, "Action is unavailable")
	user_repo = UserRepository(User)
	return await user_repo.get_objects(out_schema=UserDTO, session=db_session)
