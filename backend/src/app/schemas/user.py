import uuid
from pydantic import BaseModel, EmailStr


class AbstractUserDTO(BaseModel):
	id: int
	first_name: str
	middle_name: str | None
	last_name: str
	email: EmailStr
	password: str


class UserDTO(AbstractUserDTO):
	id: uuid.UUID = uuid.uuid4()
	telegram_nickname: str
	phone: str
	work_org_id: uuid.UUID | None = None
	position_id: uuid.UUID | None = None
