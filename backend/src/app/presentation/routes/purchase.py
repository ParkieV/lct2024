from fastapi import APIRouter, Depends, HTTPException, Request, status
from jwt import InvalidTokenError

from app.persistence.repositories.pg_repository import PurchasePositionRepository, PurchaseRepository
from app.persistence.sqlalc_models import Purchase, PurchasePosition
from app.schemas.purchase import CreatePurchaseBodyDTO, CreatePurchasePositionBodyDTO, PositionDTO, PurchaseDTO
from app.services.pg_service import PostgresServiceFacade
from app.shared.logger import logger
from app.shared.jwt import JWT

router = APIRouter(prefix="/purchase")

@router.post("/position",
			 dependencies=[Depends(JWT.check_access_token)],
			 summary="Create new purchase")
async def create_purchase_position(body: CreatePurchasePositionBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	print(payload.user_id != str(body.id))
	if "add_user" not in payload.rights and payload.user_id != str(body.id):
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Start create user")
		purchase_repo = PurchasePositionRepository(PurchasePosition)

		logger.debug("Start insert object")
		await purchase_repo.insert_object(body, out_schema=PositionDTO, session=db_session)
	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")

@router.post("/",
			 dependencies=[Depends(JWT.check_access_token)],
			 summary="Create new purchase")
async def create_purchase(body: CreatePurchaseBodyDTO, *, request: Request, db_session = Depends(PostgresServiceFacade.get_async_session)):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")
	print(payload.user_id != str(body.id))
	if "add_user" not in payload.rights and payload.user_id != str(body.id):
		raise HTTPException(403, "Action is unavailable")

	try:
		logger.debug("Start create user")
		purchase_repo = PurchaseRepository(Purchase)
		logger.debug("Start check user in DB")
		if await purchase_repo.get_object_by_id(body.id_pk, out_schema=PurchaseDTO, session=db_session, joins=Purchase.positions):
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
								detail="User is existing")

		logger.debug("Start insert object")
		await purchase_repo.insert_object(body, out_schema=PurchaseDTO, session=db_session)
	except HTTPException as err:
		raise err
	except Exception as err:
		raise HTTPException(status_code=500, detail=f"{err.__class__.__name__}: {err}")



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

