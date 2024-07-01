from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from authentication import create_jwt_token
from dependencies import get_db
from schemas.sellers import Seller, SellerCreate, SellerGet, SellerLogin
from sqlalchemy.orm import Session
from crud import seller_crud

router = APIRouter(prefix="/seller")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post(
    "/",
    response_model=Seller
)
async def create_seller(
    seller: SellerCreate, db: Session = Depends(get_db)
) -> Seller:
    final_seller = await seller_crud.crud.create(db=db, seller=seller)
    return final_seller

@router.get(
    "/",
    response_model=Seller
)
async def get_seller(
    email: str, db: Session = Depends(get_db)
) -> Seller:
    final_seller = await seller_crud.crud.get_by_email(db=db, email=email)
    return final_seller

@router.post(
    "/login",
)
async def seller_login(seller: SellerLogin, db: Session = Depends(get_db)):
    seller_info = await seller_crud.crud.get_by_email(db=db, email=seller.email)
    if not seller_info:
        return "unauthorized"
    if seller_info.password == seller.password:
        token = create_jwt_token(seller_info.id, seller_info.password, is_seller=True)
        seller_info.token = token;
        return seller_info
    else:
        return {"msg": "unauthorized"}

