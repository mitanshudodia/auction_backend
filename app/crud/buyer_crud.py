from typing import Any, Dict, List, Optional, Union

from db import models
from schemas import buyers, bids, transaction

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import func, case, select, insert
from fastapi import HTTPException


class CrudBuyer():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Buyer]:
        result = db.query(models.Buyer).get(id)
        return result

    async def get_by_email(self, db: Session, email: str) -> Optional[List[models.Buyer]]:
        result = db.query(models.Buyer).filter_by(email=email).all()
        return result

    async def create(self, db: Session, buyer: Union[buyers.BuyerCreate, Dict[str, Any]]):

        if isinstance(buyer, dict):
            buyer_data = buyer.copy()
        else:
            buyer_data = buyer.model_dump(exclude_unset=True)

        # Check if email already exists
        existing_buyer = db.query(models.Buyer).filter(models.Buyer.email == buyer_data['email']).first()
        if existing_buyer:
            raise HTTPException(status_code=400, detail="Email already exists")

        db_buyer = models.Buyer(**buyer_data)
        db_buyer.balance = 0
        db.add(db_buyer)
        db.commit()
        db.refresh(db_buyer)
        return db_buyer
    
    async def update(self, db: Session, buyer: Union[buyers.BuyerUpdate, Dict[str, Any]]):
        if isinstance(buyer, dict):
            buyer_data = buyer.copy()
        else:
            buyer_data = buyer.model_dump(exclude_unset=True)
        db_buyer = await db.query(models.Buyer).get(id)
        for field, value in buyer_data.items():
            if hasattr(db_buyer, field):
                setattr(db_buyer, field, value)
        db.commit()
        db.refresh(db_buyer)
        return db_buyer
    
    async def delete_by_id(self, db: Session, buyer: Union[buyers.BuyerDelete, Dict[str, Any]]):
        if buyer.id:
            db_buyer = await self.get_by_id(buyer.id)
        elif buyer.email:
            db_buyer = await self.get_by_email(buyer.email)
        else:
            raise Exception("Either id or email of buyer is required")
        db.delete(db_buyer)
        db.commit()
        return db_buyer

    async def get_combined_highest_bid_count(self, db: Session, buyer_id: int) -> int:
        combined_bids = (
        select(
            models.Bid.auction_good_id,
            func.max(models.Bid.bid_amount).label("highest_bid"),
            func.max(
                case(
                    (models.Bid.buyer_id == buyer_id, models.Bid.bid_amount),
                    else_=None
                )
            ).label("highest_buyer_bid")
        )
        .group_by(models.Bid.auction_good_id)
        .cte("combined_bids")
        )

        query = (
            select(func.count())
            .select_from(combined_bids)
            .where(combined_bids.c.highest_bid == combined_bids.c.highest_buyer_bid)
        )

        # Fetch all results at once (assuming your database supports it)
        results = db.execute(query)

        # Extract the scalar value (count)
        count = results.scalar()
        query2 = (
            select(func.count(models.Bid.id))
            .where(models.Bid.buyer_id == buyer_id)
        )
    
        result2 = db.execute(query2)
        count2 = result2.scalar()
        query3 = (
        select(models.Buyer.balance)
        .where(models.Buyer.id == buyer_id)
        )
    
        result3 = db.execute(query3)
        balance = result3.scalar()


        return [{'label' : 'Active Bids', 'value' : count}, {'label': 'Total Bids Placed', 'value' : count2}, {'label' : 'Account Balance', 'value' : balance}]

    async def get_buyer_dashboard_table(self, db: Session, buyer_id: int) -> list:
        subquery_c = (
            select(
                models.Bid.auction_good_id.label('auction_id'),
                func.max(models.Bid.bid_amount).label('current_bid'),
                func.count(models.Bid.id).label('total_bids')
            )
            .where(models.Bid.buyer_id == buyer_id)
            .group_by(models.Bid.auction_good_id)
            .cte('c')
        )

        subquery_d = (
            select(
                models.Bid.auction_good_id.label('auction_id'),
                func.max(models.Bid.bid_amount).label('current_bid')
            )
            .group_by(models.Bid.auction_good_id)
            .cte('d')
        )

        query = (
            select(
                models.AuctionGood.id,
                models.Good.name,
                models.AuctionGood.end_time,
                subquery_c.c.current_bid,
                subquery_c.c.total_bids,
                subquery_d.c.current_bid.label('highest_bid'),
                models.AuctionGood.amount_paid,
                models.AuctionGood.winner_id,
                models.AuctionGood.closed,
            )
            .join(models.Good, models.Good.id == models.AuctionGood.good_id)
            .join(subquery_c, subquery_c.c.auction_id == models.AuctionGood.id)
            .join(subquery_d, subquery_d.c.auction_id == subquery_c.c.auction_id)
        )

        result = db.execute(query)
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "item": row[1],
                "timeLeft": row[2],
                "currentBid": row[3],
                "totalBids": row[4],
                "highestBidder": row[5],
                "amount_paid": row[6],
                "winner_id": row[7],
                "closed": row[8]
            }
            for row in rows
        ]

    def transaction_id_exists(self, db: Session, transaction_id: str, buyer: int, amount: float, transaction_type: str) -> bool:
        result = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first() is not None
        if result:
            return None
        else:
            stmt = insert(models.Transaction).values(
            buyer=buyer,
            amount=amount,
            transaction_id=transaction_id,
            transaction_type=transaction_type
            )
            db.execute(stmt)
            db.commit()
            return True
            

    async def increment_buyer_balance(self, db: Session, buyer_id: int, amount: float) -> buyers:
        buyerOBJ = db.query(models.Buyer).filter(models.Buyer.id == buyer_id).first() or None
        if buyerOBJ:
            buyerOBJ.balance += amount
            db.commit()
            db.refresh(buyerOBJ)
            return buyerOBJ
        else:
            return None

    async def get_by_id(self, db: Session, id: str) -> Optional[List[models.Buyer]]:
        result = db.query(models.Buyer).filter(models.Buyer.id==id).first()
        return result

    async def decriment_buyer_balance(self, db: Session, buyer_id: int, amount: float) -> buyers:
        buyerOBJ = db.query(models.Buyer).filter(models.Buyer.id == buyer_id).first() or None
        amount = amount / 10
        if buyerOBJ:
            buyerOBJ.balance -= amount
            db.commit()
            db.refresh(buyerOBJ)
            return buyerOBJ
        else:
            return None

    def get_auction_good_details(self, db: Session, auction_good_id: int):
        # Define the query
        query = (
            select(models.AuctionGood.sold_price, models.Good.name, models.Good.description)
            .join(models.Good, models.AuctionGood.good_id == models.Good.id)
            .where(models.AuctionGood.id == auction_good_id)
        )
        
        # Execute the query
        result = db.execute(query).first()
        
        if not result:
            return None
        
        # Parse the result
        sold_price, name, description = result
        
        return {
            "sold_price": sold_price,
            "name": name,
            "description": description
        }




crud = CrudBuyer()