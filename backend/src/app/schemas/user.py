import uuid
from pydantic import BaseModel, EmailStr


class AbstractUserDTO(BaseModel):
	id: uuid.UUID = uuid.uuid4()
	first_name: str
	middle_name: str | None
	last_name: str
	email: EmailStr
	password: str


class UserDTO(AbstractUserDTO):
	telegram_nickname: str
	phone: str
	work_org_id: uuid.UUID | None = None
	position: str | None
	rights: str | None


class CreateRequestBodyDTO(UserDTO):
	pass

class UpdateRequestBodyDTO(BaseModel):
	id: uuid.UUID | None
	first_name: str | None = None
	middle_name: str | None = None
	last_name: str | None = None
	email: EmailStr | None = None
	password: str | None = None
	telegram_nickname: str | None = None
	phone: str | None = None
	work_org_id: uuid.UUID | None = None
	position: str | None = None
	rights: str | None = None
