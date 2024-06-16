from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.persistence.sqlalc_models import User
from app.persistence.repositories.pg_repository import UserRepository
from app.presentation.routes.balance import router as balance_router
from app.presentation.routes.purchase import router as purchase_router
from app.schemas.user import CreateRequestBodyDTO, UpdateRequestBodyDTO, UserDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.jwt import JWT
from app.shared.logger import logger

router = APIRouter(prefix="/user")

router.include_router(balance_router, tags=["User balances"])
router.include_router(purchase_router, tags=["User purchases"])


@router.post("/",
			 dependencies=[Depends(JWT.check_access_token)],
			 tags=["User CRUD"])
async def create_user(body: CreateRequestBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	if "add_user" not in payload.rights and payload.user_id != body.id:
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
async def update_user(body: UpdateRequestBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	print(payload.user_id != str(body.id))
	if "add_user" not in payload.rights and payload.user_id != str(body.id):
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Start update user")
		user_repo = UserRepository(User)

		logger.debug("Start update object")
		await user_repo.update_object_by_id(payload.user_id, body, session=db_session)
	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")

