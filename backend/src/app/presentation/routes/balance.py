
from fastapi import APIRouter, Depends, HTTPException, Request

from app.persistence.repositories.pg_repository import BalanceRepository
from app.persistence.sqlalc_models import Balance
from app.schemas.balance import BalanceDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.jwt import JWT
from app.shared.logger import logger


router = APIRouter(prefix="/balance")


@router.get("/balances",
			dependencies=[Depends(JWT.check_access_token)],
			response_model=list[BalanceDTO] | None,
			summary="Check user balance")
async def user_balances(*, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)) -> list[BalanceDTO] | None:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		logger.debug("Getting balances")
		balance_repo = BalanceRepository(Balance)
		return await balance_repo.get_objects_by_user_id(user_id=payload.user_id, out_schema=BalanceDTO, session=db_session)

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")


@router.post("/",
			dependencies=[Depends(JWT.check_access_token)],
			summary="Add user balance")
async def add_user_balance(body: BalanceDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	if not body.user_id:
		body.user_id = payload.user_id

	try:
		logger.debug("Start create balance")
		balance_repo = BalanceRepository(Balance)

		logger.debug("Insert balance into DB")
		return await balance_repo.insert_object(body, out_schema=BalanceDTO, session=db_session)

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")
