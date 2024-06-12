from typing import Any
import requests
from fastapi import APIRouter, HTTPException, status

from app.shared.config import SERVER_SETTINGS
from app.shared.logger import logger

router = APIRouter(prefix="/search")

@router.get("/catalog",
			response_model= dict[str, Any],
			summary="Get references to the search query")
async def catalog(prompt: str) -> dict[str, Any]:
	try:
		result = requests.post(f"{SERVER_SETTINGS.ml_uri}/v1/ml/show_reference", params={"prompt": prompt}).json()

		logger.debug(f"Refereces result: {result}")
		print(f"Refereces result: {result}")

		answer = {prompt: result["values"]}

		return answer
	except Exception as err:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail=err)

