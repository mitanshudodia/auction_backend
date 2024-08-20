from os import name
from typing import Any, Dict, Optional, Union

from db import models
from schemas import category

from sqlalchemy.orm import Session
from sqlalchemy import func, case, select, insert, desc

class CrudCategory():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Category]:
        result = db.query(models.Category).get(id)
        return result

    async def get_all(self, db: Session) -> models.Category:
        result = db.query(models.Category).all()
        return result

    async def create(self, db: Session, category: Union[category.CategoryOperations, Dict[str, Any]]):
        if isinstance(category, dict):
            category_data = category.copy()
        else:
            category_data = category.model_dump(exclude_unset=True)
        category_db = models.Category(**category_data)
        db.add(category_db)
        db.commit()
        db.refresh(category_db)
        return category_db
    
    async def delete_by_name(self, db: Session, category: Union[category.CategoryOperations, Dict[str, Any]]):
        if category.name:
            db_seller = db.query(models.Category).filter_by(name=name).first()
        else:
            raise Exception("Either id or email of seller is required")
        db.delete(db_seller)
        db.commit()
        return db_seller

    def get_active_auction_goods_by_seller(self, db: Session, seller_id: int, limit: int):
        query = (
            select(models.AuctionGood, models.Good)
            .join(models.Good, models.AuctionGood.good_id == models.Good.id)
            .where(models.AuctionGood.closed == False, models.AuctionGood.seller_id == seller_id)
            .limit(limit)
        )
        return db.execute(query).all()

    def get_active_auction_goods_by_category(self, db: Session, category_id: int, limit: int):
        query = (
            select(models.AuctionGood, models.Good)
            .join(models.Good, models.AuctionGood.good_id == models.Good.id)
            .where(models.AuctionGood.closed == False, models.Good.category_id == category_id)
            .limit(limit)
        )
        return db.execute(query).all()

    def get_auction_goods_with_bids(self, db: Session, category_id: int, product_name: str, seller_id: int, limit: int = None, orderByType: str = "priceHighToLow"):
        subquery = (
            select(
                models.Bid.auction_good_id,
                func.count(models.Bid.id).label("bid_count"),
                func.max(models.Bid.bid_amount).label("current_price")
            )
            .group_by(models.Bid.auction_good_id)
            .subquery()
        )

        query = (
            select(models.AuctionGood, models.Good, models.Seller, subquery.c.bid_count, subquery.c.current_price)
            .join(models.Good, models.AuctionGood.good_id == models.Good.id)
            .join(subquery, models.AuctionGood.id == subquery.c.auction_good_id, isouter=True)
            .join(models.Seller, models.AuctionGood.seller_id == models.Seller.id)
            .where(models.AuctionGood.closed == False)
            
        )
        if category_id is not None:
            query = query.where(models.Good.category_id == category_id) 

        if product_name is not None:
            query = query.where(models.Good.name.like("%" + product_name + "%") ) 
            print("%" + product_name + "%")
        
        if seller_id is not None:
            query = query.where(models.Good.seller_id == seller_id ) 

        if limit:
            query = query.limit(limit)
        
        match orderByType:
            case "priceHighToLow":
                query = query.order_by(desc(subquery.c.current_price))
            case "priceLowToHigh":
                query = query.order_by(subquery.c.current_price)
            case "endDateHighToLow":
                query = query.order_by(desc(models.AuctionGood.end_time))
            case "endDateHighToLow":
                query = query.order_by(models.AuctionGood.end_time)

        
        return db.execute(query).all()

crud = CrudCategory()