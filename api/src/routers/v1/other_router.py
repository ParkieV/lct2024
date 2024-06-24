from fastapi import APIRouter, HTTPException, Depends, Query
from matplotlib import pyplot as plt

from api.src.configurations.users import get_user_session
from api.src.services.ml_crud import is_regular
from api.src.schemas.schemas import RegularitySchema, UserPickSchema



other_router = APIRouter(
    tags=['Other Endpoints'],
    prefix='/other'
)

plt.switch_backend('Agg')



@other_router.get("/leftover_name")
def get_leftover_name(user_id: str = Query(...), user_session=Depends(get_user_session)):
    return user_session['ml_service'].leftover_name


@other_router.get("/check_regularity", response_model=RegularitySchema)
def check_regularity(user_id: str = Query(...), user_session=Depends(get_user_session)):
    schema = RegularitySchema(is_regular=is_regular(user_session['ml_service']))

    return schema


@other_router.get("/get_user_pick_info", response_model=UserPickSchema)
def get_user_pick_info(user_id: str = Query(...), user_session=Depends(get_user_session)):
    return user_session['ml_service'].get_user_pick_info()
