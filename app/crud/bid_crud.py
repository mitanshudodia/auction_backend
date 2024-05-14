from os import name
from typing import Any, Dict, List, Optional, Union

from db import models
from schemas import bids

from sqlalchemy.orm import Session

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

crud = CrudBid()