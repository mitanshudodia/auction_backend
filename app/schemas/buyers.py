from typing import Optional

from pydantic import BaseModel, EmailStr

class BuyerCreate(BaseModel):
    username: str
    email: EmailStr
    timezone: str
    full_name: str
    password: str

class BuyerUpdate(BaseModel):
    id: int
    timezone: str
    full_name: int

class BuyerDelete(BaseModel):
    id: Optional[int]
    email: Optional[str]

class Buyer(BaseModel):
    id: int
    username: str
    email: EmailStr
    timezone: str
    full_name: str
    password: str

    class Config:
        orm_mode = True

class BuyerGet(BaseModel):
    email: str

class BuyerLogin(BaseModel):
    email: EmailStr
    password: str