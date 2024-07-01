from typing import Optional

from pydantic import BaseModel, EmailStr

class BuyerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    Address: str

class BuyerUpdate(BaseModel):
    id: int
    full_name: int

class BuyerDelete(BaseModel):
    id: Optional[int]
    email: Optional[str]

class Buyer(BaseModel):
    id: int
    email: EmailStr
    password: str
    name: str
    Address: str

    class Config:
        orm_mode = True

class BuyerGet(BaseModel):
    email: str

class BuyerLogin(BaseModel):
    email: EmailStr
    password: str