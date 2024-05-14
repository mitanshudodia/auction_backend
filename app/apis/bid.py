from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from schemas.bids import BidsCreate, Bid
from sqlalchemy.orm import Session
from crud import bid_crud, auction_crud
from authentication import get_current_user

router = APIRouter(prefix="/bid")

@router.post(
    "/",
)
async def create_bid(
    bid: BidsCreate, db: Session = Depends(get_db), buyer = Depends(get_current_user)
):
    if buyer["is_seller"]:
        raise HTTPException(403, "Only Buyers can Place the bid")
    all_bids = await bid_crud.crud.get_by_auction_id(db=db, auction_id=bid.auction_good_id)
    all_bids.sort(key=lambda x: x.bid_amount, reverse=True)
    if len(all_bids) > 0 and all_bids[0].buyer_id == buyer["id"]:
        raise HTTPException(400, "You are the highest bidder, so you cannot outbid yourself")
    if len(all_bids) > 0 and bid.bid_amount <= all_bids[0].bid_amount:
        raise HTTPException(400, "Bid amount should be more than current highest bid amount")
    auction = await auction_crud.crud.get_auction_by_id(db=db, auction_id=bid.auction_good_id)
    if bid.bid_amount < auction.initial_price:
        raise HTTPException(400, "Your price should be more than initial price")
    result = await bid_crud.crud.create(db=db, bid=bid, buyer_id=buyer["id"])
    return result

@router.get(
    "/get-highest-bid",
)
async def get_highest_bid(
    auction_id: int, db: Session = Depends(get_db)
):
    all_bids = await bid_crud.crud.get_by_auction_id(db=db, auction_id=auction_id)
    all_bids.sort(key=lambda x: x.bid_amount, reverse=True)
    highest_bid = all_bids[0]
    return {"bid_amount": highest_bid, "buyer_name": highest_bid.buyer.username }