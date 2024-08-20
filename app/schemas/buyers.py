from typing import Optional

from pydantic import BaseModel, EmailStr

class BuyerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: str
    

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
    address: str
    balance: float

    class Config:
        orm_mode = True

class BuyerGet(BaseModel):
    email: str

class BuyerGetId(BaseModel):
    id: int

class BuyerLogin(BaseModel):
    email: EmailStr
    password: str