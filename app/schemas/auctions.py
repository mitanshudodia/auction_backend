from datetime import datetime
from typing import Optional
from dateutil.parser import parse
from datetime import datetime, date, time

from pydantic import BaseModel, EmailStr, NaiveDatetime, FutureDatetime, field_validator

class AuctionCreate(BaseModel):
    start_time: str
    end_time: datetime
    initial_price: float
    good_id: int
    seller_id: int
    lot_size: int
    start_date: str
    # @field_validator('start_time', mode="after")
    # def parse_start_date(cls, value):
    #     return parse(value)
    
    # @field_validator('end_time', mode="after")
    # def parse_end_date(cls, value):
    #     return parse(value)


class AuctionUpdate(BaseModel):
    id: int
    description: str
    start_time: datetime
    end_time: datetime
    initial_price: float
    lot_size: int
    # @field_validator('start_time', mode="after")
    # def parse_start_date(cls, value):
    #     return parse(value)
    
    # @field_validator('end_time', mode="after")
    # def parse_end_date(cls, value):
    #     return parse(value)

class AuctionGetorDelete(BaseModel):
    id: Optional[int]
    good_id: Optional[int]


class Auction(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    closed: Optional[bool] = False
    initial_price: float
    sold_price: Optional[float]
    good_id: int
    winner_id: Optional[int]
    seller_id: int
    lot_size: int
    # @field_validator('start_time', mode="after")
    # def parse_start_date(cls, value):
    #     return parse(value)
    
    # @field_validator('end_time', mode="after")
    # def parse_end_date(cls, value):
    #     return parse(value)
class AddBidTransactionRequest(BaseModel):
    auction_good_id: int
    buyer_id: int
    amount: float
    transaction_id: str
    transaction_type: str
    
class UpdateEndTimeRequest(BaseModel):
    auction_good_id: int



    class Config:
        orm_mode = True
