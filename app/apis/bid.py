from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from schemas.bids import BidsCreate, Bid, UnholdAmountRequest
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

@router.post("/cancel_buyer_bid")
async def unhold_amount(bid: UnholdAmountRequest, db: Session = Depends(get_db)):
    reserved_amount = bid_crud.crud.get_reserved_amount(db, bid.auction_good_id, bid.buyer_id)
    
    if reserved_amount <= 0:
        raise HTTPException(status_code=400, detail="No reserved amount found")
    
    # Update buyer balance
    buyer = bid_crud.crud.update_buyer_balance(db, bid.buyer_id, reserved_amount)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    # Add new transaction
    new_transaction = bid_crud.crud.add_transaction(db, bid.transaction_id, "UNHOLD", bid.auction_good_id, bid.buyer_id, reserved_amount)
    
    # Delete bids for the given auction_good_id and buyer_id
    bid_crud.crud.delete_bids(db, bid.auction_good_id, bid.buyer_id)
    
    return {
        "buyer_id": buyer.id,
        "new_balance": buyer.balance,
        "transaction": {
            "transaction_id": new_transaction.transaction_id,
            "transaction_type": new_transaction.transaction_type,
            "auction_good": new_transaction.auction_good,
            "buyer": new_transaction.buyer,
            "amount": new_transaction.amount
        }
    }



