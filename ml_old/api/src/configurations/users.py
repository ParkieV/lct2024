from fastapi import Depends, FastAPI, HTTPException, Request, Query
from api.src.services.user_pick_ml_service import UserPickMLService

user_sessions = {}

def get_user_session(user_id: str = Query(...)):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID query parameter missing")
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    return user_sessions[user_id]

def get_ml_service(user_session=Depends(get_user_session)):
    user_pick = user_session.get('user_pick')
    if 'ml_service' not in user_session:
        if not user_pick:
            raise HTTPException(status_code=400, detail="User pick not provided")
        user_session['ml_service'] = UserPickMLService(user_pick)
    return user_session['ml_service']