from fastapi import APIRouter

from apis import auction, buyers, category, goods, sellers, bid

final_router = APIRouter()

final_router.include_router(auction.router)
final_router.include_router(buyers.router)
final_router.include_router(category.router)
final_router.include_router(goods.router)
final_router.include_router(sellers.router)
final_router.include_router(bid.router)