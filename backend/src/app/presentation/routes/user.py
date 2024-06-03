from fastapi import APIRouter

router = APIRouter(prefix="/user")

@router.get("/")
async def user_info():
    return {"message": "Hello man"}
