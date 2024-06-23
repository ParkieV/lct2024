from fastapi import APIRouter

from .v1.matching_router import matching_router
from .v1.forecast_router import forecast_router
from .v1.other_router import other_router
from .v1.analytics_pick_router import analytics_router
from .v1.analytics_all_router import analytics_all_router
from .v1.speech2text_router import s2t_router

# v1_router = APIRouter(tags=["v1"], prefix="/api/v1/ml")
v1_router = APIRouter(tags=["v1"], prefix="/v1/ml")

v1_router.include_router(matching_router)
v1_router.include_router(forecast_router)
v1_router.include_router(other_router)
v1_router.include_router(analytics_router)
v1_router.include_router(analytics_all_router)
v1_router.include_router(s2t_router)

@v1_router.get("/")
async def root():
    return {'message': 'Hello world!'}
