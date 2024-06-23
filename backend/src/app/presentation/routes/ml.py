import io
import json
from typing import Any
from app.schemas.token import SpeechRequestDTO
from fastapi.responses import StreamingResponse
import requests
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from urllib.parse import quote

from app.shared.config import SERVER_SETTINGS
from app.shared.logger import logger
from app.shared.jwt import JWT


router = APIRouter(prefix="/search")

@router.get("/catalog",
			dependencies=[Depends(JWT.check_access_token)],
			response_model= dict[str, Any],
			summary="Get references to the search query")
async def get_references_catalog(prompt: str, *, request: Request) -> dict[str, Any]:
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/matching/show_reference", params={"prompt": prompt,
																								 "user_id": payload.user_id}).json()

		logger.debug(f"Refereces result: {result}")
		print(f"Refereces result: {result}")

		if "values" in result.keys():
			answer = {prompt: result["values"]}
		else:
			answer = {prompt: []}

		return answer
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.post("/set_user_pick",
			dependencies=[Depends(JWT.check_access_token)],
			 summary="")
async def set_user_pick(user_pick: str, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		result = requests.post(f"{SERVER_SETTINGS.ml_uri}/v1/ml/matching/set_user_pick", params={"user_pick": user_pick,
																								 "user_id": payload.user_id}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/leftover_name",
			dependencies=[Depends(JWT.check_access_token)],
			summary="shows the name of the items that are left in stock")
async def get_leftover_name(*, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/other/leftover_name", {"user_id": payload.user_id}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/regular",
			dependencies=[Depends(JWT.check_access_token)],
			summary="Check if purchase is regular")
async def is_regular(*, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")

	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/other/check_regularity", params={"user_id": payload.user_id}).json()

		print(f"result {result}")

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/user_pick_info",
			dependencies=[Depends(JWT.check_access_token)],
			summary="Get STE, SPGZ name and code about user pick")
async def get_user_pick_info(*, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/other/get_user_pick_info", params={"user_id": payload.user_id}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/leftover_info",
			dependencies=[Depends(JWT.check_access_token)])
async def get_leftover_info(*, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics/leftover_info", params={"user_id": payload.user_id}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/history",
			dependencies=[Depends(JWT.check_access_token)])
async def get_user_pick_history(n: int, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics/history", params={"user_id": payload.user_id, "n": n})

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/debit_credit_info",
			dependencies=[Depends(JWT.check_access_token)])
async def get_debit_credit_info(credit: bool, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics/debit_credit_info", params={"user_id": payload.user_id, "credit": credit}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/purchase_stats",
			dependencies=[Depends(JWT.check_access_token)])
async def get_purchase_stats(period: int, summa: bool, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics/purchase_stats", params={"period": period, "summa": summa, "user_id": payload.user_id}).json()

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/all/history",
			dependencies=[Depends(JWT.check_access_token)])
async def get_all_purchases_history(n: int, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics_all/history", params={"n": n})

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)


@router.get("/all/purchase_stats",
			dependencies=[Depends(JWT.check_access_token)])
async def get_all_purchase_stats(period: int, summa: bool, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.get(f"{SERVER_SETTINGS.ml_uri}/v1/ml/analytics_all/purchase_stats", params={"period": period, "summa": summa})

		return result
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)

@router.post("/transcribe_speech",
			dependencies=[Depends(JWT.check_access_token)])
async def get_text_from_speech(body: SpeechRequestDTO, *, request: Request):
	if not (payload := request.state.token_payload):
		raise HTTPException(500, "Can't find token payload")


	try:
		result = requests.post(f"{SERVER_SETTINGS.ml_uri}/v1/ml/s2t/transcribe",
			params={"user_id": payload.user_id},
			json={"audio": body.speech_file})
		return Response(content=json.dumps(result.json()), media_type="application/json")
	except HTTPException as http_err:
		raise http_err
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)
