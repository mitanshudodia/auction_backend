from typing import Dict, Union, Annotated, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
import shutil
import os
from db.models import Good
from dependencies import get_db
from schemas.goods import Goods, GoodsCreate, GoodsGetorDelete, GoodsUpdate
import datetime
from sqlalchemy.orm import Session
from crud import goods_crud
from authentication import get_current_user
import json

router = APIRouter(prefix="/goods")

@router.post("/")
async def add_good(
    name: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    productLocation: str = Form(...),
    productImages: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    seller = Depends(get_current_user)
) -> Union[Goods, Dict]:
    # Process and save images
    saved_image_paths = []
    for file in productImages:
        print(file.filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        file_name2 = os.path.splitext(file.filename)[0]
        new_filename = f"{file_name2}{timestamp}{file_extension}"
        file_path = os.path.join('C:\\Totem Server\\Port2PortV1\\public\\product_images', new_filename )
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_image_paths.append(new_filename)
    # Create the good in the database
    good = GoodsCreate(
        name=name,
        description=description,
        category_id=category_id,
        location=productLocation,
        images_link= json.dumps(saved_image_paths)
    )
    result = await goods_crud.crud.create(db=db, goods=good, seller_id=seller["id"])
    return {
    "Message" : "succsess"
    }

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
async def good_update(    name: str = Form(...),    description: str = Form(...),    category_id: int = Form(...),id: int = Form(...), db: Session= Depends(get_db), seller = Depends(get_current_user)):
    good: Good = await goods_crud.crud.get_by_id(db,id)
    good_id = id
    if good.seller_id != seller["id"]:
        raise HTTPException(403, "You are not Authorized to perform this action")
    good = await goods_crud.crud.update(db, name, description, category_id, good_id)
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
async def get_by_user(seller_id: int, db: Session = Depends(get_db)):
    current_data = await goods_crud.crud.get_by_user_id(db=db, user_id=seller_id)
    return current_data
