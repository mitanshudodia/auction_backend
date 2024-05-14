import datetime
from typing import List, Awaitable
from fastapi import APIRouter, Depends
from dependencies import get_db
from schemas.auctions import Auction, AuctionCreate, AuctionGetorDelete, AuctionUpdate
from schemas import sellers
from sqlalchemy.orm import Session
from crud import auction_crud, seller_crud
from authentication import get_current_user
from utils import convert_from_utc_to_local, convert_to_utc
import pytz

router = APIRouter(prefix="/auction")

@router.post(
    "/",
    response_model=Auction
)
async def create_auction(
    auction: AuctionCreate, db: Session = Depends(get_db), seller=Depends(get_current_user)
) -> Auction:
    seller_data: sellers.Seller = await seller_crud.crud.get_by_id(db=db, id=seller["id"])
    timezone = seller_data.timezone
    # auction.start_time = await convert_to_utc(timezone=timezone, date_time=auction.start_time)
    # auction.end_time = await convert_to_utc(timezone=timezone, date_time=auction.end_time)
    result = await auction_crud.crud.start_auction(db=db, auction=auction)
    result.start_time = await convert_from_utc_to_local(local_timezone=timezone, utc_time=result.start_time)
    result.end_time = await convert_from_utc_to_local(local_timezone=timezone, utc_time=result.end_time)
    result.start_time = result.start_time.isoformat()
    result.end_time = result.end_time.isoformat()
    return result

@router.get(
    "/active-auctions",
    response_model=List[Auction]
)
async def get_active_auctions( db: Session = Depends(get_db), seller=Depends(get_current_user)
) -> List[Auction]:
    seller_data: sellers.Seller = await seller_crud.crud.get_by_id(db=db, id=seller["id"])
    timezone = seller_data.timezone
    all_auctions = await auction_crud.crud.get_open_auction(db=db)
    active_auctions: List[Auction] = []
    current_time = datetime.datetime.now(pytz.UTC).replace(tzinfo=None)
    for auction in all_auctions:
        if auction.start_time <= current_time and current_time <= auction.end_time:
            auction.start_time = await convert_from_utc_to_local(local_timezone=timezone, utc_time=auction.start_time)
            auction.end_time = await convert_from_utc_to_local(local_timezone=timezone, utc_time=auction.end_time)
            active_auctions.append(auction)
    active_auctions.sort(key= lambda x: x.start_time)
    return active_auctions

@router.put(
    "/",
    response_model=Auction
)
async def good_update(auction: AuctionUpdate, db: Session= Depends(get_db), seller=Depends(get_current_user)):
        if (auction.start_time or auction.end_time):
            seller_data: sellers.Seller = await seller_crud.crud.get_by_id(seller["id"])
            timezone = seller_data.timezone
            if auction.start_time:
                auction.start_time = await convert_to_utc(timezone=timezone, date_time=auction.start_time)
            if auction.end_time:
                auction.end_time = await convert_to_utc(timezone=timezone, date_time=auction.end_time)
        current_data = await auction_crud.crud.update_auction(db=db, auction=auction, seller_id=seller["id"])
        return current_data
