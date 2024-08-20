from os import name
from typing import Any, Dict, List, Optional, Union

from db import models
from schemas import bids, transaction, buyers

from sqlalchemy.orm import Session
from sqlalchemy import func, case, select, insert, desc

class CrudBid():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Bid]:
        result = db.query(models.Bid).get(id)
        return result

    async def get_all(self, db: Session) -> models.Bid:
        result = db.query(models.Bid).all()
        return result
    
    async def get_by_auction_id(self, db: Session, auction_id:int) -> List[models.Bid]:
        result = db.query(models.Bid).filter_by(auction_good_id=auction_id).all()
        return result

    async def create(self, db: Session, bid: Union[bids.BidsCreate, Dict[str, Any]], buyer_id: int):
        if isinstance(bid, dict):
            bid_data = bid.copy()
        else:
            bid_data = bid.model_dump(exclude_unset=True)
        bid_data["buyer_id"] = buyer_id
        bid_db = models.Bid(**bid_data)
        db.add(bid_db)
        db.commit()
        db.refresh(bid_db)
        return bid_db

    def get_reserved_amount(self, db: Session, auction_good_id: int, buyer_id: int) -> float:
        result = db.query(func.sum(models.Bid.bid_amount)).filter(
            models.Bid.auction_good_id == auction_good_id,
            models.Bid.buyer_id == buyer_id
        ).scalar()
        return result or 0.0

    def update_buyer_balance(self, db: Session, buyer_id: int, amount: float):
        buyer = db.query(models.Buyer).filter(models.Buyer.id == buyer_id).first()
        if not buyer:
            print("couldn't find buyer")
            return None
        buyer.balance += amount / 10
        db.commit()
        db.refresh(buyer)
        print("updated buyer balance" )
        return buyer

    def add_transaction(self, db: Session, transaction_id: str, transaction_type: str, auction_good_id: int, buyer_id: int, amount: float):
        new_transaction = models.Transaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            auction_good=auction_good_id,
            buyer=buyer_id,
            amount=amount
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction

    def delete_bids(self, db: Session, auction_good_id: int, buyer_id: int):
        db.query(models.Bid).filter(models.Bid.auction_good_id == auction_good_id, models.Bid.buyer_id == buyer_id).delete()
        db.commit()


crud = CrudBid()