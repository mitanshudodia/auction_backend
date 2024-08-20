from typing import Optional

from pydantic import BaseModel, EmailStr

class GoodsCreate(BaseModel):
    name: str
    description: str
    category_id: int
    images_link: str
    

class GoodsUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        required = ['id']

class GoodsGetorDelete(BaseModel):
    id: int


class Goods(BaseModel):
    id: int
    name: str
    description: str
    seller_id: int
    category_id: int
    document_link: str
    images_link: Optional[str] = None
    specs: Optional[str] = None

class Config:
    orm_mode = True