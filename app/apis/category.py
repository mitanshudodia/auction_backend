from typing import List
from fastapi import APIRouter, Depends
from dependencies import get_db
from schemas.category import CategoryOperations, Category
from sqlalchemy.orm import Session
from crud import category_crud
from authentication import get_current_user

router = APIRouter(prefix="/category")

@router.post(
    "/",
    response_model=Category
)
async def create_category(
    category: CategoryOperations, db: Session = Depends(get_db)
) -> Category:
    result = await category_crud.crud.create(db=db, category=category)
    return result

@router.get(
    "/",
)
async def get_category( db: Session = Depends(get_db)
) -> List[Category]:
    final_buyer = await category_crud.crud.get_all(db=db)
    return final_buyer

@router.delete(
    "/",
)
async def delete_category(
    category: CategoryOperations, db: Session = Depends(get_db)
):
    deleted_category = await category_crud.crud.delete_by_name(db=db, category=category)  
    return deleted_category