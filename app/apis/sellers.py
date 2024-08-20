from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from authentication import create_jwt_token
from dependencies import get_db
from schemas.sellers import Seller, SellerCreate, SellerGet, SellerLogin, EmailSchema, ResetSchema
from sqlalchemy.orm import Session
from crud import seller_crud
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from db import models
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/seller")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

conf = ConnectionConfig(
    MAIL_USERNAME="rishadgandhy@toteminteractive.in",
    MAIL_PASSWORD="Interactive@2024",
    MAIL_FROM="rishadgandhy@toteminteractive.in",
    MAIL_PORT=465,
    MAIL_SERVER="toteminteractive.in",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,   
    VALIDATE_CERTS=True
)

async def send_reset_email(email: str, token: str):
    reset_link = f"http://localhost:3000/seller/change-password/{token}"
    
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click the following link to reset your password: {reset_link}",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

def create_reset_token(db: Session, seller: Seller):
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=1)
    seller.reset_token = token
    seller.reset_token_expiration = expiration
    db.commit()
    
    return token

@router.post("/request-password-reset")
async def request_password_reset(email_schema: EmailSchema, db: Session = Depends(get_db)):
    seller = db.query(models.Seller).where(models.Seller.email == email_schema.email).first()
    
    if seller is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = create_reset_token(db, seller)
    #seller.reset_token = token
    db.commit()
    await send_reset_email(seller.email, token)
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(resetSchema: ResetSchema, db: Session = Depends(get_db)):
    seller = db.query(models.Seller).where(models.Seller.reset_token == resetSchema.token).first()
    
    if seller is None or seller.reset_token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Here you would hash the new password and update the user's record
    # user.password = hash_password(new_password)
    seller.password = resetSchema.new_password
    seller.reset_token = None
    seller.reset_token_expiration = None
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.get("/emailTest")
async def send_email():
    emailSent = await send_reset_email("rishad.gandhy@gmail.com","asdasdasdasd21322")
    return True;

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

