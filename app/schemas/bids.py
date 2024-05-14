from typing import Optional

from pydantic import BaseModel, EmailStr

class BidsCreate(BaseModel):
    bid_amount: float
    auction_good_id: int

class BidderInfo(BaseModel):
    id: int
    seller_id: int
    seller_name: str
    bid_amount: float

class Bid(BaseModel):
    id: int
    bid_amount: float
    auction_good_id: int
    buyer_id: int

    class Config:
        orm_mode = True
