from typing import Any, Dict, List, Optional, Union
from unittest import result
from fastapi import FastAPI, Depends

from db import models
from schemas import auctions, bids, goods

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, select

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
    
    async def get_seller_statistics(self, db: Session, seller_id: int) -> dict:
        count_active_listings = db.query(func.count(models.AuctionGood.id)).filter(
            models.AuctionGood.seller_id == seller_id,
            models.AuctionGood.closed == False
        ).scalar()

        count_total_listings = db.query(func.count(models.AuctionGood.id)).filter(
            models.AuctionGood.seller_id == seller_id,
        ).scalar()

        sum_query = db.query(func.sum(models.AuctionGood.sold_price)).filter(
            models.AuctionGood.seller_id == seller_id,
            models.AuctionGood.closed == True
        ).scalar()
        
        return {
            "active_listings": count_active_listings,
            "total_listings": count_total_listings,
            "total_sales": sum_query
        }

    async def get_seller_auction_data(self, db: Session, seller_id: int) -> list:
        # Subquery to get bid count and max bid amount per auction_good_id
        subquery = (
            select(
                func.count(models.Bid.id).label("bid_count"),
                func.max(models.Bid.bid_amount).label("bid_amount"),
                models.Bid.auction_good_id
            )
            .group_by(models.Bid.auction_good_id)
            .alias("c")
        )
        # Main query to select desired fields
        query = (
            select(
                models.Good.name,
                models.AuctionGood.initial_price,
                models.AuctionGood.end_time,
                subquery.c.bid_count,
                subquery.c.bid_amount
            )
            .select_from(models.AuctionGood)
            .join(models.Good, models.Good.id == models.AuctionGood.good_id)
            .outerjoin(subquery, subquery.c.auction_good_id == models.AuctionGood.id)
            .filter(models.AuctionGood.seller_id == seller_id)
        )
        results = db.execute(query).fetchall()
        return [{"name": row.name, "initial_price": row.initial_price, "end_time": row.end_time, "bid_count": row.bid_count, "bid_amount": row.bid_amount} for row in results]


crud = CrudAuction()