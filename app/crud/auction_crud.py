import datetime
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

    async def get_auctions_to_close(self, db: Session) -> List[auctions.Auction]:
        now = datetime.datetime.utcnow()
        result = db.query(models.AuctionGood) \
            .where(models.AuctionGood.end_time <= now.strftime('%Y-%m-%d %H:%M:%S')) \
            .filter_by(closed=False).all()
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
            .where(models.AuctionGood.closed == False)
            .join(models.Good, models.Good.id == models.AuctionGood.good_id)
            .outerjoin(subquery, subquery.c.auction_good_id == models.AuctionGood.id)
            .filter(models.AuctionGood.seller_id == seller_id)
        )
        results = db.execute(query).fetchall()
        return [{"name": row.name, "basePrice": row.initial_price, "endTime": row.end_time, "bid_count": row.bid_count, "currentBid": row.bid_amount} for row in results]

    async def get_seller_auction_past_data(self, db: Session, seller_id: int) -> list:
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
            .where(models.AuctionGood.closed == True)
            .join(models.Good, models.Good.id == models.AuctionGood.good_id)
            .outerjoin(subquery, subquery.c.auction_good_id == models.AuctionGood.id)
            .filter(models.AuctionGood.seller_id == seller_id)
        )
        results = db.execute(query).fetchall()
        return [{"name": row.name, "basePrice": row.initial_price, "endTime": row.end_time, "bid_count": row.bid_count, "currentBid": row.bid_amount} for row in results]

    async def get_auction_good_details(self,db: Session, auction_good_id: int) -> dict:
        subquery = (
            select(func.max(models.Bid.bid_amount).label('max_bid_price'), models.Bid.auction_good_id)
            .where(models.Bid.auction_good_id == auction_good_id)
            .group_by(models.Bid.auction_good_id)
            .alias('C')
        )

        query = (
            select(models.AuctionGood, models.Good, models.Seller, subquery.c.max_bid_price)
            .join(models.Good, models.AuctionGood.good_id == models.Good.id)
            .join(models.Seller, models.AuctionGood.seller_id == models.Seller.id)
            .outerjoin(subquery, subquery.c.auction_good_id == models.AuctionGood.id)
            .where(models.AuctionGood.id == auction_good_id)
        )
        
        result = db.execute(query)
        row = result.fetchone()
        
        if row:
            auction_good, good, seller, max_bid_price  = row
            return {
                    "auction_id": auction_good.id,
                    "start_time": auction_good.start_time,
                    "end_time": auction_good.end_time,
                    "closed": auction_good.closed,
                    "initial_price": auction_good.initial_price,
                    "sold_price": auction_good.sold_price,
                    "good_id": auction_good.good_id,
                    "winner_id": auction_good.winner_id,
                    "seller_id": auction_good.seller_id,
                    "lot_size": auction_good.lot_size,
                    "start_date": auction_good.start_date,
                    "good_id": good.id,
                    "good_name": good.name,
                    "good_description": good.description,
                    "good_images_link": good.images_link,
                    "good_category_id" : good.category_id,
                    "good_document_link" : good.document_link,
                    "good_specs" : good.specs,
                    "seller_name" : seller.name,
                    "seller_rating" : seller.rating,
                    "current_price" : max_bid_price
            }
        return None
    def get_sum_bid_amount(self, db: Session, buyer_id: int, auction_good_id: int) -> float:
        result = db.query(func.sum(models.Bid.bid_amount)).filter(
            models.Bid.buyer_id == buyer_id,
            models.Bid.auction_good_id == auction_good_id
        ).scalar()
        return result if result else 0.0

    def add_bid(self, db: Session, auction_good_id: int, buyer_id: int, amount: float):
        new_bid = models.Bid(
            bid_amount=amount,
            auction_good_id=auction_good_id,
            buyer_id=buyer_id
        )
        db.add(new_bid)
        db.commit()
        db.refresh(new_bid)
        return new_bid

    def add_transaction(self, db: Session, transaction_id: str, amount: float, transaction_type: str, auction_good_id: int, buyer_id: int):
        amount = amount / 10
        new_transaction = models.Transaction(
            transaction_id=transaction_id,
            amount=amount,
            transaction_type=transaction_type,
            auction_good=auction_good_id,
            buyer=buyer_id,
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction

crud = CrudAuction()