import io
from typing import List

from fastapi import APIRouter
from starlette.responses import Response
from api.src.services.ml_service import matching_service_reference, init_models
from fastapi.responses import StreamingResponse


ml_router = APIRouter(
    tags=['ML'],
    prefix='/ml'
)

init_models()

@ml_router.post("/show_reference")
def show_reference(prompt: str):
    return matching_service_reference(prompt)






