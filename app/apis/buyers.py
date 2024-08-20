from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from schemas.buyers import Buyer, BuyerCreate, BuyerGet, BuyerLogin, BuyerGetId, EmailSchema, ResetSchema
from schemas.address import AddressCreate
from schemas import address
from schemas.transaction import IncrementBalanceRequest
from sqlalchemy.orm import Session
from crud import buyer_crud, transaction_crud
from authentication import create_jwt_token
from db import models
import secrets
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


router = APIRouter(prefix="/buyer")

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
    reset_link = f"http://localhost:3000/buyer/change-password/{token}"
    
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click the following link to reset your password: {reset_link}",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

def create_reset_token(db: Session, buyer: Buyer):
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=1)
    buyer.reset_token = token
    buyer.reset_token_expiration = expiration
    db.commit()
    
    return token

@router.post("/request-password-reset")
async def request_password_reset(email_schema: EmailSchema, db: Session = Depends(get_db)):
    buyer = db.query(models.Buyer).where(models.Buyer.email == email_schema.email).first()
    
    if buyer is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = create_reset_token(db, buyer)
    #seller.reset_token = token
    db.commit()
    await send_reset_email(buyer.email, token)
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(resetSchema: ResetSchema, db: Session = Depends(get_db)):
    buyer = db.query(models.Buyer).where(models.Buyer.reset_token == resetSchema.token).first()
    
    if buyer is None or buyer.reset_token_expiration < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Here you would hash the new password and update the user's record
    # user.password = hash_password(new_password)
    buyer.password = resetSchema.new_password
    buyer.reset_token = None
    buyer.reset_token_expiration = None
    db.commit()
    
    return {"message": "Password reset successfully"}


@router.post(
    "/",
    response_model=Buyer
)
async def create_buyer(
    buyer: BuyerCreate, db: Session = Depends(get_db)
) -> Buyer:
    try:
        final_buyer = await buyer_crud.crud.create(db=db, buyer=buyer)
        return final_buyer
    except HTTPException as e:
        raise e

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

@router.get("/combined_highest_bid_count")
async def combined_highest_bid_count(buyer_id: int, db: Session = Depends(get_db)):
    count = await buyer_crud.crud.get_combined_highest_bid_count(db, buyer_id)
    return count

@router.get("/get_buyer_dashboard_table")
async def auction_details(buyer_id: int, db: Session = Depends(get_db)):
    details = await buyer_crud.crud.get_buyer_dashboard_table(db, buyer_id)
    return details

@router.post("/increment_balance")
async def increment_balance(request: IncrementBalanceRequest, db: Session = Depends(get_db)):
    buyerOBJ = ''
    if buyer_crud.crud.transaction_id_exists(db, request.transaction_id, request.buyer, request.amount, request.transaction_type):
        buyerOBJ = await buyer_crud.crud.increment_buyer_balance(
        db, request.buyer, request.amount
        )
        print(buyerOBJ)
        if buyerOBJ is None:
            raise HTTPException(status_code=404, detail="Buyer not found")
        return {"buyer_id": buyerOBJ.id, "new_balance": buyerOBJ.balance}
    return {"msg" : "Error, payment information already added"}

@router.get(
        "/getById",
        response_model=Buyer
    )
async def get_buyerById(
        id: int, db: Session = Depends(get_db)
    ) -> Buyer:
        final_buyer = await buyer_crud.crud.get_by_id(db=db, id=id)
        return final_buyer

@router.get("/good_sale_details")
async def get_auction_good_details(auction_good_id: int, db: Session = Depends(get_db)):
    details = buyer_crud.crud.get_auction_good_details(db, auction_good_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Auction good not found")
    
    return details

@router.post('/add_address')
def add_address(address: AddressCreate, db: Session = Depends(get_db)):
    
    
    addressOBJ = models.Address(
        address_line_1=address.address_line_1,
        address_line_2=address.address_line_2,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        buyer_id=address.buyer_id
    )

    db.add(addressOBJ)
    db.commit()

    return {"message": "Address added successfully!", "status" : "OK"}

