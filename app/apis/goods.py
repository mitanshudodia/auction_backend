from typing import Dict, Union
from fastapi import APIRouter, Depends, HTTPException
from db.models import Good
from dependencies import get_db
from schemas.goods import Goods, GoodsCreate, GoodsGetorDelete, GoodsUpdate
from sqlalchemy.orm import Session
from crud import goods_crud
from authentication import get_current_user

router = APIRouter(prefix="/goods")

@router.post(
    "/",
    response_model=Goods
)
async def add_good(
    good: GoodsCreate, db: Session = Depends(get_db), seller = Depends(get_current_user)
) -> Union[Goods, Dict]:
    if not seller["is_seller"]:
        raise HTTPException(403, "Only Sellers can add the goods")
    result = await goods_crud.crud.create(db=db, goods=good, seller_id=seller["id"])
    return result

@router.get(
    "/",
    response_model=Goods
)
async def get_good(
    good_id: int, db: Session = Depends(get_db)
) -> Goods:
    final_buyer = await goods_crud.crud.get_by_id(db=db, id=good_id)
    return final_buyer

@router.put(
    "/",
    response_model=Goods
)
async def good_update(good: GoodsUpdate, db: Session= Depends(get_db), seller = Depends(get_current_user)):
    good: Good = await goods_crud.crud.get_by_id(good.id)
    if good.seller_id != seller["id"]:
        raise HTTPException(403, "You are not Authorized to perform this action")
    good = await goods_crud.crud.update(db=db, goods=good)
    return good

@router.delete(
    "/",
    response_model=Goods
)
async def delete(good: GoodsGetorDelete, db: Session=Depends(get_db), seller = Depends(get_current_user)):
    current_data = await goods_crud.crud.get_by_id(db=db, id=good.id)
    if current_data.seller_id == seller["id"]:
        good = await goods_crud.crud.delete(db=db, goods=good)
        return good
    raise HTTPException(status_code=403, detail="Unauthorized")

@router.get(
    "/seller-goods"
)
async def get_by_user(db: Session = Depends(get_db), seller = Depends(get_current_user)):
    current_data = await goods_crud.crud.get_by_user_id(db=db, user_id=seller["id"])
    return current_data
