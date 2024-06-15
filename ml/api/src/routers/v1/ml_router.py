import io
from typing import List

from fastapi import APIRouter, HTTPException
from starlette.responses import Response
from api.src.services.ml_service import matching_service_reference, init_models, is_regular, get_leftovers, pick_history
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
import pandas as pd
from tempfile import NamedTemporaryFile


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


@ml_router.get("/check_regular")
def get_regular(user_pick: str):

    return is_regular(user_pick)


@ml_router.get("/get_history")
def get_last_n_history(user_pick: str):
    df = pick_history(user_pick)

    if df.empty:
        raise HTTPException(status_code=404, detail="No history found for the specified pick")

    # Save the DataFrame to a temporary Excel file
    with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        with pd.ExcelWriter(tmp.name, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        # Return the file as a download
        return FileResponse(path=tmp.name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=f"{user_pick}_history.xlsx")



# @ml_router.get("/get_sales")
# def get_regular(user_pick: str):

#     return pick_sales(user_pick)
