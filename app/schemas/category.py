from typing import Optional

from pydantic import BaseModel, EmailStr

class CategoryOperations(BaseModel):
    name: str

class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True