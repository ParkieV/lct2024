import io
from typing import List

from fastapi import APIRouter
from starlette.responses import Response
from api.src.services.ml_service import matching_service_reference, init_models, is_regular, get_leftovers
from fastapi.responses import StreamingResponse


ml_router = APIRouter(
    tags=['ML'],
    prefix='/ml'
)

init_models()

@ml_router.get("/show_reference")
def show_reference(prompt: str):
    return matching_service_reference(prompt, 15)

@ml_router.get("/return_leftovers")
def return_leftovers(user_pick: str):
    return get_leftovers(user_pick)
    

@ml_router.get("/prompt_regular")
def get_regular(user_pick: str):
    
    return is_regular(user_pick)
    



