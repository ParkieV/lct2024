from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.routes.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	# Before server started
#	await MySQLTools.check_connection()
#	RedisTools.check_connection()
	yield
	# After server has shuted down
	logging.info('Server shutting down.\n\n\n')




app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods="*",
	allow_headers="*",
)
app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000)
