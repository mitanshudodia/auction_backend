import datetime
from typing import List, Awaitable
from fastapi import APIRouter, Depends
from dependencies import get_db
from schemas.auctions import Auction, AuctionCreate, AuctionGetorDelete, AuctionUpdate, AddBidTransactionRequest, UpdateEndTimeRequest
from schemas import sellers, bids
from sqlalchemy.orm import Session
from crud import auction_crud, seller_crud, buyer_crud
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
    start_date = auction.start_date
    start_time = auction.start_time
    auction.start_time = start_date + " " +start_time
    auction.end_time = auction.end_time
    result = await auction_crud.crud.start_auction(db=db, auction=auction)
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
    current_time = datetime.datetime.now(pytz.UTC)
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

@router.get("/getSellerStatistics")
async def get_seller_statistics_route(seller_id: int, db: Session = Depends(get_db)):
    return await auction_crud.crud.get_seller_statistics(db, seller_id)

@router.get("/getSellerAuctionData")
async def get_seller_auction_data(seller_id: int, db: Session = Depends(get_db)):
    return await auction_crud.crud.get_seller_auction_data(db, seller_id)

@router.get("/getSellerAuctionPastData")
async def get_seller_auction_past_data(seller_id: int, db: Session = Depends(get_db)):
    return await auction_crud.crud.get_seller_auction_past_data(db, seller_id)

@router.get("/", response_model=Auction)
async def get_auction(auction_id: int, db: Session = Depends(get_db)):
    return await auction_crud.crud.get_auction_by_id(db, auction_id)

@router.get("/auction_good_details")
async def auction_good_details(auction_good_id: int, db: Session = Depends(get_db)):
    details = await auction_crud.crud.get_auction_good_details(db, auction_good_id)
    if details:
        return details
    return {"error": "AuctionGood not found"}

@router.get("/get_sum_bid_amount")
async def get_sum_bid_amount(buyer_id: int, auction_good_id: int, db: Session = Depends(get_db)):
    sum_bid_amount = auction_crud.crud.get_sum_bid_amount(db, buyer_id, auction_good_id)
    if sum_bid_amount is None:
        raise HTTPException(status_code=404, detail="No bids found for the given buyer and auction good.")
    return {"sum_bid_amount": sum_bid_amount}


@router.post("/add_bid_transaction")
async def add_bid_transaction(request: AddBidTransactionRequest, db: Session = Depends(get_db)):
    # Add the bid
    new_bid = auction_crud.crud.add_bid(db, request.auction_good_id, request.buyer_id, request.amount)
    
    # Add the transaction
    new_transaction = auction_crud.crud.add_transaction(
        db,
        request.transaction_id,
        request.amount,
        request.transaction_type,
        request.auction_good_id,
        request.buyer_id
    )
    await buyer_crud.crud.decriment_buyer_balance(db,request.buyer_id,request.amount)
    return {
        "bid": {
            "id": new_bid.id,
            "auction_good_id": new_bid.auction_good_id,
            "buyer_id": new_bid.buyer_id,
            "bid_amount": new_bid.bid_amount
        },
        "transaction": {
            "id": new_transaction.id,
            "transaction_id": new_transaction.transaction_id,
            "amount": new_transaction.amount,
            "transaction_type": new_transaction.transaction_type,
            "auction_good": new_transaction.auction_good,
            "buyer": new_transaction.buyer,
            "created_on": new_transaction.created_on
        }
    }


@router.post("/auction-goods/update-end-time")
def update_auction_good_end_time(
    request: UpdateEndTimeRequest,
    db: Session = Depends(get_db)
):
    print(request.auction_good_id)
    response = auction_crud.crud.update_auction_good_end_time(db, request.auction_good_id)
    return response
    
