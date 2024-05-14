from typing import Optional

from pydantic import BaseModel, EmailStr

class SellerCreate(BaseModel):
    name: str
    email: EmailStr
    timezone: str
    contact: int
    rating: float
    password: str

class SellerUpdate(BaseModel):
    id: int
    timezone: str
    contact: int
    rating: float

class SellerDelete(BaseModel):
    id: Optional[int]
    email: Optional[str]

class Seller(BaseModel):
    id: int
    name: str
    email: EmailStr
    timezone: str
    contact: int
    rating: Optional[float]
    password: str

    class Config:
        orm_mode = True

class SellerGet(BaseModel):
    email: str

class SellerLogin(BaseModel):
    email: EmailStr
    password: str