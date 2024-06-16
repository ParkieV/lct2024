import uuid
from pydantic import BaseModel, Field


class OrganizationDTO(BaseModel):
    value: uuid.UUID = Field(default=uuid.uuid4(), validation_alias="id")
    label: str = Field(validation_alias="name")


class OrganizationListDTO(BaseModel):
    orgList: list[OrganizationDTO]
