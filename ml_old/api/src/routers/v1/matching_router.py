from fastapi import APIRouter, HTTPException, Depends, Query
from matplotlib import pyplot as plt

from api.src.configurations.users import get_user_session
from api.src.services.user_pick_ml_service import UserPickMLService
from api.src.services.ml_crud import matching_service_reference



matching_router = APIRouter(
    tags=['Matching Service'],
    prefix='/matching'
)

plt.switch_backend('Agg')

@matching_router.get("/show_reference")
def show_reference(prompt: str, user_id: str = Query(...), user_session=Depends(get_user_session)):
    return matching_service_reference(prompt)


@matching_router.post("/set_user_pick/")
async def set_user_pick(user_pick: str, user_id: str = Query(...), user_session=Depends(get_user_session)):
    user_session['user_pick'] = user_pick
    user_session['ml_service'] = UserPickMLService(user_pick)
    return {"message": "User pick set successfully"}
