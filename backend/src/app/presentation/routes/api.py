
from fastapi import APIRouter

from app.presentation.routes.auth import router as auth_router
from app.presentation.routes.organization import router as org_router
from app.presentation.routes.user import router as user_router
from app.presentation.routes.ml import router as ml_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router, tags=["System for accessing internal resources"])
api_router.include_router(ml_router, tags=["ML"])
api_router.include_router(user_router, tags=["User CRUD"])
api_router.include_router(org_router, tags=["Organization CRUD"])

