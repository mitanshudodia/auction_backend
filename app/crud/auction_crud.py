from typing import Any, Dict, List, Optional, Union
from unittest import result

from db import models
from schemas import auctions

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

class CrudAuction():
    async def start_auction(self, db: Session, auction: Union[auctions.AuctionCreate, Dict[str, Any]]):
        if isinstance(auction, dict):
            auction_data = auction.copy()
        else:
            auction_data = auction.model_dump(exclude_unset=True)
        db_auction = models.AuctionGood(**auction_data)
        db.add(db_auction)
        db.commit()
        db.refresh(db_auction)
        return db_auction
    
    async def get_open_auction(self, db: Session) -> List[auctions.Auction]:
        result = db.query(models.AuctionGood).filter_by(closed=False).all()
        return result
    
    async def get_auction_by_id(self, db: Session, auction_id: int) -> auctions.Auction:
        result = db.query(models.AuctionGood).get(auction_id)
        return result
    
    async def update_auction(self, db: Session, auction: Union[auctions.AuctionUpdate, Dict[str, Any]], seller_id: int) -> auctions.Auction:
        if isinstance(auction, dict):
            auction_data = auction.copy()
        else:
            auction_data = auction.model_dump(exclude_unset=True)
        db_auction = await db.query(models.AuctionGood).filter_by(id=auction.id)
        if db_auction.get("good").get("seller_id") != seller_id:
            raise Exception("Not Authorized")
        for field, value in auction_data.items():
            if hasattr(db_auction, field):
                setattr(db_auction, field, value)
        db.commit()
        db.refresh(db_auction)
        return db_auction
    
    async def delete_auction(self, db: Session, auction: Union[auctions.AuctionGetorDelete, Dict[str, Any]]):
        if auction.id:
            result = db.query(models.AuctionGood).get(id)
        else:
            raise Exception("Id is required")
        db.delete(result)
        db.commit()
        return result
    

crud = CrudAuction()