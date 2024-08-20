from typing import List
from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_db
from schemas.category import CategoryOperations, Category
from sqlalchemy.orm import Session
from crud import category_crud
from authentication import get_current_user
from urllib.error import HTTPError

router = APIRouter(prefix="/category")

@router.post(
    "/",
    response_model=Category
)
async def create_category(
    category: CategoryOperations, db: Session = Depends(get_db)
) -> Category:
    result = await category_crud.crud.create(db=db, category=category)
    return result

@router.get(
    "/",
)
async def get_category( db: Session = Depends(get_db)
) -> List[Category]:
    final_buyer = await category_crud.crud.get_all(db=db)
    return final_buyer

@router.delete(
    "/",
)
async def delete_category(
    category: CategoryOperations, db: Session = Depends(get_db)
):
    deleted_category = await category_crud.crud.delete_by_name(db=db, category=category)  
    return deleted_category

@router.get("/get_active_auction_goods_by_seller")
async def get_active_auction_goods(seller_id: int, db: Session = Depends(get_db)):
    auction_goods = category_crud.crud.get_active_auction_goods_by_seller(db, seller_id)
    if not auction_goods:
        raise HTTPException(status_code=404, detail="No active auction goods found for the given seller_id")
    
    return [
        {
            "auction_good": {
                "id": item.AuctionGood.id,
                "start_time": item.AuctionGood.start_time,
                "end_time": item.AuctionGood.end_time,
                "closed": item.AuctionGood.closed,
                "initial_price": item.AuctionGood.initial_price,
                "sold_price": item.AuctionGood.sold_price,
                "good_id": item.AuctionGood.good_id,
                "winner_id": item.AuctionGood.winner_id,
                "seller_id": item.AuctionGood.seller_id,
                "lot_size": item.AuctionGood.lot_size,
                "start_date": item.AuctionGood.start_date,
                "good_name" : item.Good.name,

            }
        } for item in auction_goods
    ]

@router.get("/get_active_auction_goods_by_category")
async def get_active_auction_goods(category_id: int, db: Session = Depends(get_db)):
    auction_goods = category_crud.crud.get_active_auction_goods_by_category(db, category_id)
    if not auction_goods:
        raise HTTPException(status_code=404, detail="No active auction goods found for the given seller_id")
    
    return [
        {
            "auction_good": {
                "id": item.AuctionGood.id,
                "start_time": item.AuctionGood.start_time,
                "end_time": item.AuctionGood.end_time,
                "closed": item.AuctionGood.closed,
                "initial_price": item.AuctionGood.initial_price,
                "sold_price": item.AuctionGood.sold_price,
                "good_id": item.AuctionGood.good_id,
                "winner_id": item.AuctionGood.winner_id,
                "seller_id": item.AuctionGood.seller_id,
                "lot_size": item.AuctionGood.lot_size,
                "start_date": item.AuctionGood.start_date,
                "good_name" : item.Good.name,

            }
        } for item in auction_goods
    ]

@router.get("/get_auction_goods_with_bids")
async def get_auction_goods_with_bids(
    category_id = None,
    product_name = None,
    seller_id = None,
    limit = None,
    orderByType = "priceHighToLow",
    db: Session = Depends(get_db)
):
    auction_goods = category_crud.crud.get_auction_goods_with_bids(db, category_id,product_name, seller_id,limit, orderByType)
    if not auction_goods:
        return {"status" : "failed", "message" : "No data to return"}    
    return [
        {
                "id": item.AuctionGood.id,
                "start_time": item.AuctionGood.start_time,
                "end_time": item.AuctionGood.end_time,
                "closed": item.AuctionGood.closed,
                "initial_price": item.AuctionGood.initial_price,
                "sold_price": item.AuctionGood.sold_price,
                "good_id": item.AuctionGood.good_id,
                "winner_id": item.AuctionGood.winner_id,
                "seller_id": item.AuctionGood.seller_id,
                "lot_size": item.AuctionGood.lot_size,
                "start_date": item.AuctionGood.start_date,
                "good_name":  item.Good.name,
                "seller_name" : item.Seller.name,
                "images" : item.Good.images_link,
                "bid_count": item.bid_count,
                "current_price": item.current_price
        } for item in auction_goods
    ]
