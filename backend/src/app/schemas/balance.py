from decimal import Decimal
import uuid
from pydantic import BaseModel

class BalanceDTO(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    name: str
    amount: Decimal
    user_id: uuid.UUID

