from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse


from .src.routers import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_application():
    return FastAPI(
        title="ML API",
        description="Сервис ML для кейса №2 хакатона Лидеры Цифровой Трансформации",
        version="1.0.1",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

app = create_application()

origins = [
    'http://localhost',
    'http://localhost:8080',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


def _configure():
    app.include_router(v1_router)

_configure()