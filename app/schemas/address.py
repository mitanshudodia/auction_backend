from typing import Optional

from pydantic import BaseModel, EmailStr

class AddressCreate(BaseModel):
    address_line_1: str
    address_line_2: str
    city: str
    state: str
    postal_code: str
    buyer_id: str