from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from schemas.buyers import Buyer, BuyerCreate, BuyerGet, BuyerLogin
from sqlalchemy.orm import Session
from crud import buyer_crud
from authentication import create_jwt_token

router = APIRouter(prefix="/buyer")

@router.post(
    "/",
    response_model=Buyer
)
async def create_buyer(
    buyer: BuyerCreate, db: Session = Depends(get_db)
) -> Buyer:
    final_buyer = await buyer_crud.crud.create(db=db, buyer=buyer)
    return final_buyer

@router.get(
    "/",
    response_model=Buyer
)
async def get_buyer(
    buyer: BuyerGet, db: Session = Depends(get_db)
) -> Buyer:
    final_buyer = await buyer_crud.crud.get_by_email(db=db, buyer=buyer.email)
    return final_buyer

@router.post(
    "/login",
)
async def buyer_login(buyer: BuyerLogin, db: Session = Depends(get_db)):
    buyer_info = await buyer_crud.crud.get_by_email(db=db, email=buyer.email)
    if len(buyer_info) == 0:
        raise HTTPException(404, "User not found")
    if buyer_info[0].password == buyer.password:
        token = create_jwt_token(buyer_info[0].id, buyer_info[0].password)
        returnVar = buyer_info[0]
        returnVar.token = token
        return returnVar
