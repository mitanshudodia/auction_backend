from typing import Optional

from pydantic import BaseModel, EmailStr

class IncrementBalanceRequest(BaseModel):
    buyer: int
    amount: float
    transaction_id: str
    transaction_type: str
