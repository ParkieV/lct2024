from io import BytesIO
import base64

from fastapi import APIRouter, HTTPException, Depends, Query
import pandas as pd
from tempfile import NamedTemporaryFile
from fastapi.responses import FileResponse
from matplotlib import pyplot as plt

from api.src.configurations.users import get_user_session
from api.src.schemas.schemas import LeftoverSchema, PurchasesSchema, DebitCreditSchema, ExcelSchema


analytics_router = APIRouter(
    tags=['Analytics Endpoints for User Pick'],
    prefix='/analytics'
)

plt.switch_backend('Agg')


@analytics_router.get("/leftover_info", response_model=LeftoverSchema)
def get_leftover_info(user_id: str = Query(...), user_session=Depends(get_user_session)):
    return user_session['ml_service'].get_leftover_info_plot()

@analytics_router.get("/history", response_model=ExcelSchema)
def get_last_n_history(user_id: str = Query(...), user_session=Depends(get_user_session), n: int = Query(...)):
    df = user_session['ml_service'].get_history(n)
    df = df.drop(columns=['year', 'quarter', 'month', 'day', 'Длительность'])

    if df.empty:
        raise HTTPException(status_code=404, detail="No history found for the specified pick")

    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)

    excel_file = base64.b64encode(buf.read()).decode('utf-8')
    return {'file': excel_file}
    

@analytics_router.get("/debit_credit_info", response_model=DebitCreditSchema)
def get_debit_credit_info(credit: bool, user_id: str = Query(...), user_session=Depends(get_user_session)):
    return user_session['ml_service'].get_credit_debit(credit)


@analytics_router.get("/purchase_stats", response_model=PurchasesSchema)
def get_purchase_stats(period: int, summa: bool, user_id: str = Query(...), user_session=Depends(get_user_session)):
    if period < 1 or period > 3:
        raise HTTPException(status_code=400, detail="Invalid period value. Must be 1, 2, or 3")
    
    return user_session['ml_service'].get_purchase_stats(period, summa)
