from typing import Optional

from pydantic import BaseModel, EmailStr

class GoodsCreate(BaseModel):
    name: str
    description: str
    company_name: str
    category_id: int

class GoodsUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        required = ['id']

class GoodsGetorDelete(BaseModel):
    id: int


class Goods(BaseModel):
    id: int
    name: str
    description: str
    company_name: str
    category_id: int
    seller_id: int
    images_link: Optional[str]

    class Config:
        orm_mode = True
