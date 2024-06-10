import uuid
from pydantic import BaseModel, EmailStr

from app.schemas.user import UserDTO


class LoginRequestBodyDTO(BaseModel):
    email: EmailStr
    password: str


class SignupRequestBodyDTO(BaseModel):
    email: EmailStr
    user: UserDTO
    password: str
