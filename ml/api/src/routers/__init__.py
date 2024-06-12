from fastapi import APIRouter

from .v1.ml_router import ml_router

v1_router = APIRouter(tags=["v1"], prefix="/api/v1")

v1_router.include_router(ml_router)
