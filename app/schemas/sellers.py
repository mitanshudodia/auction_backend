from typing import Optional

from pydantic import BaseModel, EmailStr

class SellerCreate(BaseModel):
    name: str
    companyName: str
    officeAddress: str
    email: EmailStr
    contact: int
    password: str

class SellerUpdate(BaseModel):
    id: int
    contact: int
    rating: float

class SellerDelete(BaseModel):
    id: Optional[int]
    email: Optional[str]

class Seller(BaseModel):
    id: int
    name: str
    email: EmailStr
    officeAddress: str
    contact: int
    rating: Optional[float]
    password: str
    companyName: str

    class Config:
        orm_mode = True

class SellerGet(BaseModel):
    email: str

class SellerLogin(BaseModel):
    email: EmailStr
    password: str

class EmailSchema(BaseModel):
    email: EmailStr

class ResetSchema(BaseModel):
    token: str
    new_password: str