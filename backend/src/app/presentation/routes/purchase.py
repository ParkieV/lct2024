from fastapi import APIRouter, Depends, HTTPException, Request
from jwt import InvalidTokenError

from app.persistence.repositories.pg_repository import PurchaseRepository
from app.persistence.sqlalc_models import Purchase
from app.schemas.purchase import PurchaseDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.logger import logger
from app.shared.jwt import JWT

router = APIRouter(prefix="/purchase")


@router.get("/user_purchases",
            dependencies=[Depends(JWT.check_access_token)],
            summary="Get all purchases for user")
async def user_purchases(*, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)) -> list[PurchaseDTO] | None:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		logger.debug("Getting balances")
		purchase_repo = PurchaseRepository(Purchase)
		return await purchase_repo.get_objects_by_user_id(user_id=payload.user_id, out_schema=PurchaseDTO, session=db_session)

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")

@router.get("/all_purchases",
            dependencies=[Depends(JWT.check_access_token)],
            summary="Get all purchases")
async def all_purchases(*, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)) -> list[PurchaseDTO] | None:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	if "add_user" not in payload.rights:
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Getting balances")
		purchase_repo = PurchaseRepository(Purchase)
		return await purchase_repo.get_objects(out_schema=PurchaseDTO, session=db_session, joins=Purchase.positions)

	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")

