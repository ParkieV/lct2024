from io import BytesIO
import base64

from fastapi import APIRouter, HTTPException, Depends, Query
import pandas as pd
from tempfile import NamedTemporaryFile
from fastapi.responses import FileResponse
from matplotlib import pyplot as plt

from api.src.configurations.users import get_user_session
from api.src.schemas.schemas import LeftoverSchema, PurchasesSchema,  ExcelSchema
from api.src.services.analytics_service import get_history, get_purchases

analytics_all_router = APIRouter(
    tags=['Analytics Endpoints for Everything'],
    prefix='/analytics_all'
)

plt.switch_backend('Agg')


@analytics_all_router.get("/history", response_model=ExcelSchema)
def get_last_n_history(n: int):
    df = get_history().head(n)

    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)

    excel_file = base64.b64encode(buf.read()).decode('utf-8')
    return {'file': excel_file}


@analytics_all_router.get("/purchase_stats", response_model=PurchasesSchema)
def get_purchase_stats(period: int, summa: bool):
    if period < 1 or period > 3:
        raise HTTPException(status_code=400, detail="Invalid period value. Must be 1, 2, or 3")
    
    df = get_history()
    return get_purchases(df, period, summa)
